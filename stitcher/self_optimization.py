"""
Implements stitching, and filtering functions based on a bidding concept.
"""

import logging
import networkx as nx

import stitcher

TMP = {}


class Entity(object):
    """
    An node in a graph that can bid on nodes of the request graph.
    """

    def __init__(self, name, mapping, request, container, conditions=None):
        self.name = name
        self.container = container
        self.request = request
        self.mapping = mapping
        self.bids = {}
        self.conditions = conditions or {}

    def _calc_credits(self):
        tmp = []
        for node, attr in self.request.nodes(data=True):
            if self.mapping[attr['type']] == self.container.node[self]['type']:
                # TODO - ensure no bids are added which are already done and
                # cannot be exceeded.
                # TODO: bidding concept:
                # - lg, gt, eq, neq, regex: bid if met - higher bit the bigger
                #   delta.
                # - same & diff: increase bid if other is near or away.
                # - share, nshare: (increase) bid if other entity with same
                #   attr fits/doesn't fit.
                if self.name == 'A':
                    tmp.append((node, 8))
                elif self.name == 'B':
                    tmp.append((node, 9))
                else:
                    tmp.append((node, 10))
                # calculating credits.
            else:
                pass
        if len(tmp) > 0:
            self.bids[self.name] = tmp
        logging.info(self.name + ' - current bids ' + repr(self.bids))

    def trigger(self, msg, src):
        """
        Triggers a bidding round on this entity.

        :param msg: dict containing the message from other entity.
        :param src: str indicating the src of where the message comes from.
        """
        self._calc_credits()
        logging.info(str(src) + ' -> ' + str(self.name) + ' msg: ' + str(msg))

        # let's add those I didn't know of
        mod = msg['bids'] == self.bids
        for item in msg['bids']:
            if item not in self.bids:
                # Only pick bids from other - each entity controls own bids!
                self.bids[item] = msg['bids'][item]

        # assign and optimize were needed.
        assigned = msg['assigned']
        if self.name in self.bids:
            for bid in self.bids[self.name]:
                rq_n = bid[0]  # request node
                crd = bid[1]  # bid 'credits'.
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
