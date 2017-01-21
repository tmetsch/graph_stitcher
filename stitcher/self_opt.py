"""
Module enabling self optimization of nodes in the container graph.
"""

import logging
import networkx as nx

LOG = logging.getLogger()


class Entity(object):
    """
    An entity which tries to self-optimize it's assigned resources:

    (1) by trying to offer unfit stitches to neighbours (e.g. based on mapping
        and or conditions); and
    (2) asking for stitches which make more sense.

    it does this by working with credits. Whereby the credits bid/offered are
    associated wth the "fitness" of the stitch: for a real good fit the
    entities tries to bid high; for a bad fit it doesn't try hard. While using
    the credits the entity does not need to expose many details (e.g.
    capacities) and can hide a bit of it's capabilities towards it's neighbours.

    Assumption is that all nodes in the container know about the request nodes
    that need to stitched. In future we could think about entities even change
    edges which are not stitches between request and container.
    """

    # TODO: how to simulate a trade - e.g. ask for one and give another back
    #       (ask should include the id of asking node so it can propagate
    #       through the network, so even not directly connected nodes known 
    #       about the ask. Asks should age-out however). Check gossip papers.

    # TODO: how to prevent two entities are constantly bidding for two nodes
    #       which want to share target node?

    # TODO: check if we can somehow uplift those connections for which trades
    #       between two parties always were "good". And which make sense -
    #       only offer sth to a neighbour if he theoretically could take it. 
    #       Check ant-nets/"pheromone trails".

    def __init__(self, node_name, candidate, request, stitch, conditions):
        """
        Initializes the entity.

        :param node_name: Id of the node this entity represents.
        :param candidate: A candidate graph containing both container and
            request and 'random' stitches between them.
        :param request: The request.
        :param stitch: How to stitch the types.
        :param conditions: The conditions.
        """
        # TODO: check if this should decay/increase over time etc.
        self.credits = 100
        self.node_name = node_name
        self.candidate = candidate
        self.stitch = stitch
        self.request = request
        self.condy = conditions

    def process(self):
        """
        Process this entity - find own optimal share based on fitness/utility.
        """
        offers = []  # nodes this entity doesn't want.
        asks = []  # nodes this entity wants.
        portfolio = []  # things to keep - influence the bid.
        candidates = []  # neighbors this entity can offer too.
        for ngb in nx.all_neighbors(self.candidate, self):
            if ngb.node_name in self.request:
                # add to ask, bid or portfolio list.
                tmp = self.request.node[ngb.node_name]['type']
                if self.stitch[tmp] != self.candidate.node[self]['type']:
                    offers.append((ngb, 1))  # TODO: adjust credit
            else:
                candidates.append(ngb)

        # now actually bid to neighbours
        for ngb in candidates:
            ngb.step(offers, asks, 0, self)

    def step(self, offers, asks, step_index, other_entity):
        """
        Process the offered and asks stitches.

        :param offers: The nodes in the request offered to this entity.
        :param asks: The nodes in the request asked for by another entity.
        :param step_index: Not used for now.
        :param other_entity: The entity offering to this one.
        """
        # TODO: check if step_index / id can be used to prevent ever running
        #       algorithm. Also to check if a close to 'global' optimal state
        #       is reached.

        LOG.debug('%s got offered %s and got asked for %s.',
                  self.node_name, repr(offers), repr(asks))
        for node, costs in offers:
            # decide what to do with stuff offered to me
            # TODO: include concept of trading?
            tmp = self.request.node[node.node_name]['type']
            if self.stitch[tmp] == self.candidate.node[self]['type']:
                # take it.
                self.candidate.add_edge(node, self)  # TODO: edge attributes
                self.candidate.remove_edge(node, other_entity)
                other_entity.credits += costs
                self.credits -= costs
        for node, bid in asks:
            pass

    def __repr__(self):
        return self.node_name

    def __eq__(self, other):
        if isinstance(other, str):
            if other == self.node_name:
                return True
            return False
        elif isinstance(other, Entity) and other.node_name == self.node_name:
            return True
        else:
            return False
