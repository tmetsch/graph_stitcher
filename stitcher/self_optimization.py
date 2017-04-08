"""
Implements stitching, and filtering functions based on a bidding concept.
"""

import logging
import re

import networkx as nx

import stitcher

TMP = {}

FACTOR_1 = 1.25
FACTOR_2 = 1.5


def _attribute_condy(condy, bids, param, node_attr):
    """
    Basic rules to deal with attribute conditions.
    """
    node = param[0]
    attrn = param[1][0]
    attrv = param[1][1]
    if condy == 'lg':
        # huge delta -> high bid.
        bids[node] = node_attr[attrn] - attrv + bids[node]
    elif condy == 'lt':
        # huge delta -> high bid.
        bids[node] = attrv - node_attr[attrn] + bids[node]
    elif condy == 'eq':
        # attr not present or not equal -> drop bid.
        if attrn not in node_attr or attrv != node_attr[attrn]:
            bids.pop(node)
    elif condy == 'neq':
        # attr present and equal -> drop bid.
        if attrn in node_attr and attrv == node_attr[attrn]:
            bids.pop(node)
    elif condy == 'regex':
        # attr present and reges does not match -> drop bid.
        if attrn in node_attr and not re.search(attrv, node_attr[attrn]):
            bids.pop(node)


def _same_condy(bids, param):
    flag = True
    # if I do a bid on all elements in param...
    for item in param:
        if item not in bids.keys():
            flag = False
            break
    # ... I'll increase the bids.
    if flag:
        for item in param:
            bids[item] = bids[item] * FACTOR_2


def _diff_condy(bids, assigned, param):
    # if other entity has the others - I can increase my bid for the greater
    # good.
    for item in param:
        if item not in assigned and len(assigned) != 0:
            bids[item] = bids[item] * FACTOR_2
        elif item in bids and item in assigned and len(assigned) != 0:
            bids[item] = bids[item] * FACTOR_1

    # keep highest bid - remove rest.
    keeper = max(bids, key=lambda k: bids[k] if k in param else None)
    for item in param:
        if item in bids and item != keeper:
            bids.pop(item)


def _share_condy(bids, param, container):
    attrn = param[0]
    nodes = param[1]
    # TODO: here I am


def _apply_conditions(bids, assigned, node, conditions, container):
    """
    Alter bids based on conditions.
    """
    if 'attributes' in conditions:
        for item in conditions['attributes']:
            condy = item[0]
            param = item[1]
            node_attr = container.node[node]
            _attribute_condy(condy, bids, param, node_attr)
    if 'compositions' in conditions:
        for item in conditions['compositions']:
            condy = item[0]
            param = item[1]
            if condy == 'same':
                _same_condy(bids, param)
            elif condy == 'diff':
                _diff_condy(bids, assigned, param)
            elif condy == 'share':
                _share_condy(bids, param, container)
    return bids


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

    def _calc_credits(self, assigned):
        tmp = {}
        for node, attr in self.request.nodes(data=True):
            if self.mapping[attr['type']] == self.container.node[self]['type']:
                tmp[node] = 1.0
            else:
                pass
        if len(tmp) > 0:
            self.bids[self.name] = _apply_conditions(tmp,
                                                     assigned,
                                                     self,
                                                     self.conditions,
                                                     self.container)
        logging.info(self.name + ': current bids ' + repr(self.bids))

    def trigger(self, msg, src):
        """
        Triggers a bidding round on this entity.

        :param msg: dict containing the message from other entity.
        :param src: str indicating the src of where the message comes from.
        """
        logging.info(str(src) + ' -> ' + str(self.name) + ' msg: ' + str(msg))
        assigned = msg['assigned']
        self._calc_credits(assigned)

        # let's add those I didn't know of
        mod = msg['bids'] == self.bids
        for item in msg['bids']:
            if item not in self.bids:
                # Only pick bids from other - each entity controls own bids!
                self.bids[item] = msg['bids'][item]

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
            elif msg is not None and self.name not in msg['bids'] \
                    and self.name in self.bids:
                # only call my caller back when he didn't knew me.
                neighbour.trigger(src=self.name,
                                  msg={'bids': self.bids,
                                       'assigned': assigned})
        return assigned, self.bids


class SelfOptStitcher(stitcher.Stitcher):
    """
    Stitcher based on a bidding concept.
    """

    def stitch(self, container, request, conditions=None, start=None):
        opt_graph = nx.DiGraph()
        tmp = {}
        for node, attr in container.nodes(data=True):
            tmp[node] = Entity(node, self.rels, request, opt_graph)
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
