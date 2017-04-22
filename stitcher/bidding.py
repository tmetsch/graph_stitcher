"""
Implements stitching, and filtering functions based on a bidding concept.
"""

import copy
import logging
import re

import networkx as nx

import stitcher

TMP = {}

FACTOR_1 = 1.25
FACTOR_2 = 1.5


def _other_bids(all_bids):
    """
    XXX: see if this can be simplified. Maybe by using diff struct in bids.
    """
    res = []
    for item in all_bids.values():
        for sub_item in item:
            res.append(sub_item)
    return res


def _attribute_condy(condy, my_bids, param, node_attr):
    """
    Basic rules to deal with attribute conditions.
    """
    node = param[0]
    attrn = param[1][0]
    attrv = param[1][1]
    if node not in my_bids:
        # I'm not bidding on this node - so no need to do sth.
        return

    if condy == 'lg':
        # huge delta -> high bid.
        my_bids[node] = node_attr[attrn] - attrv + my_bids[node]
    elif condy == 'lt':
        # huge delta -> high bid.
        my_bids[node] = attrv - node_attr[attrn] + my_bids[node]
    elif condy == 'eq':
        # attr not present or not equal -> drop bid.
        if attrn not in node_attr or attrv != node_attr[attrn]:
            my_bids.pop(node)
    elif condy == 'neq':
        # attr present and equal -> drop bid.
        if attrn in node_attr and attrv == node_attr[attrn]:
            my_bids.pop(node)
    elif condy == 'regex':
        # attr present and reges does not match -> drop bid.
        if attrn in node_attr and not re.search(attrv, node_attr[attrn]):
            my_bids.pop(node)


def _same_condy(my_bids, param):
    flag = True
    # if I do a bid on all elements in param...
    for item in param:
        if item not in my_bids.keys():
            flag = False
            break
    # ... I'll increase the bids.
    # TODO: only if my bid is better though...
    if flag:
        for item in param:
            my_bids[item] = my_bids[item] * FACTOR_2
    else:
        for item in param:
            # if not all can be stitched to me - I need to remove all bids.
            if item in my_bids:
                my_bids.pop(item)


def _diff_condy(my_bids, param, assigned, all_bids):
    # if other entity has the others - I can increase my bid for the greater
    # good.
    for item in param:
        if set(param) - set(assigned.keys()) == {item}:
            # if others assigned increase by factor 2
            my_bids[item] = my_bids[item] * FACTOR_2
        elif set(param) - set(_other_bids(all_bids)) == {item}:
            # if others are bid on increase by factor 1
            my_bids[item] = my_bids[item] * FACTOR_1
        elif len(set(param) - set(_other_bids(all_bids))) == 0 \
                and item in my_bids:
            # bids out for all - increase by factor 1
            my_bids[item] = my_bids[item] * FACTOR_1

    # keep highest bid - remove rest.
    keeper = max(my_bids, key=lambda k: my_bids[k] if k in param else None)
    for item in param:
        if item in my_bids and item != keeper:
            my_bids.pop(item)


def _nshare_condy(my_bids, param, assigned, node, container):
    attrn = param[0]
    attrv_assigned = None
    nodes = param[1]
    for item in nodes:
        if item in assigned and attrv_assigned is None:
            tmp = [n for n in container.nodes() if n.name == assigned[item][0]]
            attrv_assigned = container.node[tmp[0]][attrn]
        elif attrv_assigned is not None and item in my_bids \
                and container.node[node][attrn] != attrv_assigned:
            my_bids[item] = my_bids[item] * FACTOR_2

CACHE = {}


def _sub_stitch(container, request, mapping, condy):
    if (container, request) not in CACHE:
        opt_graph = nx.DiGraph()
        tmp = {}
        for node, attr in container.nodes(data=True):
            tmp[node] = Entity(str(node), mapping, request, opt_graph,
                               conditions=condy)
            opt_graph.add_node(tmp[node], attr)
        for src, trg, attr in container.edges(data=True):
            opt_graph.add_edge(tmp[src], tmp[trg], attr)

        start_node = tmp.values()[0]

        # kick off
        assign, _ = start_node.trigger({'bids': [], 'assigned': {}},
                                       'sub-init')
        CACHE[container, request] = assign

    return CACHE[(container, request)]


class Entity(object):
    """
    A node in a graph that can bid on nodes of the request graph.
    """

    def __init__(self, name, mapping, request, container, conditions=None):
        self.name = name
        self.container = container
        self.request = request
        self.mapping = mapping
        self.bids = {}
        self.conditions = conditions or {}

    def _share_condy(self, condy, param, my_bids, assigned):
        """
        If I know that mine and surrounding bids are lower than what another
        combo can offer - drop bids & assignments!
        """
        attrn = param[0]
        nodes = param[1]
        if attrn not in self.container.node[self]:
            for item in nodes:
                if item in my_bids:
                    my_bids.pop(item)
            return
        my_attrv = self.container.node[self][attrn]
        bids = self.bids

        cache = {}
        # step 1) find possible groups that I know of.
        for item in bids:
            tmp = [n for n in self.container.nodes() if n.name == item][0]
            if attrn in self.container.node[tmp]:
                attrv = self.container.node[tmp][attrn]
                if attrv not in cache:
                    cache[attrv] = [tmp]
                else:
                    cache[attrv].append(tmp)

        options = {}
        # step 2) figure out what the groups are worth.
        for item in cache:
            sub_container = nx.subgraph(self.container, cache[item])
            sub_request = nx.subgraph(self.request, nodes)
            sub_condy = copy.deepcopy(self.conditions)
            sub_condy['compositions'].remove(condy)
            assign = _sub_stitch(sub_container, sub_request, self.mapping,
                                 sub_condy)
            if assign.keys() == nodes:
                # is complete
                options[item] = sum([val[1] for val in assign.values()])
                for tmp in nodes:
                    if tmp in my_bids and self in sub_container:
                        my_bids[tmp] = my_bids[tmp] * FACTOR_2

        # step 3) drop my bids & assignments.
        res = []
        if my_attrv in options and len(options) >= 2 \
                and sorted(options, key=options.get,
                           reverse=True)[0] != my_attrv:
            for item in nodes:
                if item in my_bids:
                    my_bids.pop(item)
                    res.append(item)
            for item in nodes:
                if item in assigned and assigned[item][0] == self.name:
                    assigned.pop(item)
        return res

    def _apply_conditions(self, my_bids, assigned):
        """
        Alter bids based on conditions.
        """
        if 'attributes' in self.conditions:
            for item in self.conditions['attributes']:
                condy = item[0]
                param = item[1]
                node_attr = self.container.node[self]
                _attribute_condy(condy, my_bids, param, node_attr)
        if 'compositions' in self.conditions:
            for item in self.conditions['compositions']:
                condy = item[0]
                param = item[1]
                if condy == 'same':
                    _same_condy(my_bids, param)
                elif condy == 'diff':
                    _diff_condy(my_bids, param, assigned, self.bids)
                elif condy == 'share':
                    self._share_condy(item, param, my_bids, assigned)
                elif condy == 'nshare':
                    _nshare_condy(my_bids, param, assigned,
                                  self,
                                  self.container)
        return my_bids

    def _calc_credits(self, assigned):
        tmp = {}
        for node, attr in self.request.nodes(data=True):
            if self.mapping[attr['type']] == self.container.node[self]['type']:
                tmp[node] = 1.0
        if len(tmp) > 0:
            self.bids[self.name] = self._apply_conditions(tmp, assigned)
        logging.info(self.name + ': current bids ' + repr(self.bids))

    def trigger(self, msg, src):
        """
        Triggers a bidding round on this entity.

        :param msg: dict containing the message from other entity.
        :param src: str indicating the src of where the message comes from.
        """
        logging.info(str(src) + ' -> ' + str(self.name) + ' msg: ' + str(msg))

        # let's add those I didn't know of
        mod = msg['bids'] == self.bids
        for item in msg['bids']:
            # each entity controls own bids!
            self.bids[item] = msg['bids'][item]

        assigned = msg['assigned']
        self._calc_credits(assigned)
        # assign and optimize were needed.
        if self.name in self.bids:
            for bid in self.bids[self.name]:
                rq_n = bid  # request node
                crd = self.bids[self.name][bid]  # bid 'credits'.
                if rq_n not in assigned:
                    logging.info('Assigning: ' + rq_n + ' -> ' + self.name)
                    assigned[rq_n] = (self.name, crd)
                else:
                    if assigned[rq_n][1] < crd:
                        # my bid is better.
                        logging.info('Updated assignment: ' + rq_n + ' -> ' +
                                     self.name)
                        assigned[rq_n] = (self.name, crd)

        # communicate
        # XXX: enable async.
        for neighbour in nx.all_neighbors(self.container, self):
            if neighbour.name != src and not mod:
                # only update neighbour when there is an update to be send.
                neighbour.trigger(src=self.name,
                                  msg={'bids': self.bids,
                                       'assigned': assigned})
            elif msg is not None and msg['bids'] != self.bids:
                # only call my caller back when he didn't knew me.
                neighbour.trigger(src=self.name,
                                  msg={'bids': self.bids,
                                       'assigned': assigned})
        return assigned, self.bids

    def __repr__(self):
        return self.name


class BiddingStitcher(stitcher.Stitcher):
    """
    Stitcher based on a bidding concept where each Agent of MAS bids for nodes
    from the request graph.
    """

    def stitch(self, container, request, conditions=None, start=None):
        condy = conditions or {}
        opt_graph = nx.DiGraph()
        tmp = {}
        for node, attr in container.nodes(data=True):
            tmp[node] = Entity(str(node), self.rels, request, opt_graph,
                               conditions=condy)
            opt_graph.add_node(tmp[node], attr)
        for src, trg, attr in container.edges(data=True):
            opt_graph.add_edge(tmp[src], tmp[trg], attr)

        start_node = tmp.values()[0]
        if start is not None:
            start_node = tmp[start]

        # kick off
        assign, _ = start_node.trigger({'bids': [], 'assigned': {}}, 'init')
        tmp_graph = nx.union(container, request)
        for item in assign:
            src = item
            trg = assign[item][0]
            tmp_graph.add_edge(src, trg)

        return [tmp_graph]
