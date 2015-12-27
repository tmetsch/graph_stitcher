
import itertools
import json

import networkx as nx


class BaseWeaver(object):
    """
    Base weaver with the function which need to be implemented.
    """

    def __init__(self, filename='data/weave.json'):
        self.rels = json.load(open(filename, 'r'))

    def weave(self, landscape, request, conditions=None, filter=filter):
        """
        Weave a request graph into an existing graph landscape. Returns a set
        of possible options.

        :param landscape: A graph describing the existing landscape with
            scores.
        :param request: A graph describing the request.
        :param conditions: Dictionary with conditions - e.g. node a & b need
            to be related to node c.
        :param filter: Function which allows for filtering useless options
            upfront.
        :return: The resulting landscape(s).
        """
        res = []
        # TODO: optimize this
        # TODO: adhere conditions!
        # TODO: add filter function to eliminate non valid weaves upfront.

        # 1. find possible mappings
        tmp = {}
        for node, attr in request.nodes(data=True):
            if attr['type'] in self.rels:
                candidates = self._find_nodes(landscape,
                                              self.rels[attr['type']])
                for candidate in candidates:
                    if node not in tmp:
                        tmp[node] = [candidate]
                    else:
                        tmp[node].append(candidate)

        # TODO: allow for nodes in request not related to landscape nodes!
        # 2. find candidates
        candidate_edge_list = []
        keys = tmp.keys()
        s = []
        for key in keys:
            s.append(tmp[key])

        for edge_list in itertools.product(*s):
            j = 0
            edges = []
            for item in edge_list:
                edges.append((keys[j], item))
                j += 1
            candidate_edge_list.append(edges)

        # 3. create candidate landscapes
        tmp_graph = nx.union(landscape, request)
        for item in candidate_edge_list:
            candidate_graph = tmp_graph.copy()
            for s, t in item:
                candidate_graph.add_edge(s, t)
            res.append(candidate_graph)
        return res

    def validate(self, landscapes):
        """
        Validate a set of landscape from the weave() function. Return a
        dictionary with the index & explanatory text.

        :param landscapes: List of possible landscapes
        :return: dict with int:str.
        """
        raise NotImplementedError('Needs to be implemented...')

    def _find_nodes(self, graph, tzpe):
        res = []
        for node, values in graph.nodes(data=True):
            if values['type'] == tzpe:
                res.append(node)
        return res

    def _filter(self):
        pass


class IncomingEdgeWeaver(BaseWeaver):
    """
    Implemented simple rule to validate based on # of incoming edges.
    """

    def validate(self, landscapes, condition={}):
        """
        In case a node of a certain type has more then a threshold of incoming
        edges determine a possible weave as a bad weave.
        """
        res = {}
        i = 0
        for candidate in landscapes:
            res[i] = 'ok'
            for node, values in candidate.nodes(data=True):
                if values['type'] not in condition.keys():
                    continue
                else:
                    tmp = condition[values['type']]
                if len(candidate.in_edges(node)) >= tmp:
                    res[i] = 'node ' + str(node) + ' has to many edges: ' + \
                             str(len(candidate.in_edges(node)))
            i += 1
        return res


class NodeScoreWeaver(BaseWeaver):
    """
    Implements simple rule to validate weave based on scores & incoming edges
    of a node.
    """

    def validate(self, landscapes, condition={}):
        """
        In case a score of a node and # of incoming edges increases determine
        possible weave as a bad weave.
        """
        res = {}
        i = 0
        for candidate in landscapes:
            res[i] = 'ok'
            for node, values in candidate.nodes(data=True):
                if values['type'] not in condition.keys():
                    continue
                else:
                    tmp = condition[values['type']]
                if len(candidate.in_edges(node)) >= tmp[0] \
                        and values['score'] >= tmp[1]:
                    res[i] = 'node ' + str(node) + ' has a to high score.'
            i += 1
        return res
