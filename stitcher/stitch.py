
import itertools
import json

import networkx as nx


def filter(container, edge_list, conditions):
    """
    Default filter which scans the candidate edge list and eliminates those
    candidates which do not adhere the conditions. Following conditions are
    available:

    attributes - the target node need to have a certain attribute
    composition - two nodes need to have same target node or two nodes should
        not have the same target node.

    :param edge_list: the candidate edge list as created by stitch().
    :param conditions: dictionary containing the conditions.
    :return: The filtered edge list.
    """
    if conditions is None:
        return edge_list
    else:
        rm = []
        if 'attributes' in conditions:
            rm.extend(_attr_filter(container, edge_list, conditions))
        if 'compositions' in conditions:
            for condition in conditions['compositions']:
                para1 = conditions['compositions'][condition][0]
                para2 = conditions['compositions'][condition][1]
                if condition is 'same':
                    rm.extend(_same_filter(para1, para2, edge_list))
                if condition is 'diff':
                    rm.extend(_diff_filter(para1, para2, edge_list))
                if condition is 'share':
                    rm.extend(_share_attr(container, para1, para2, edge_list))
        for item in rm:
            try:
                edge_list.remove(item)
            except ValueError:
                pass   # multiple filters might request removal.
        return edge_list


def _attr_filter(container, candidate_list, conditions):
    """
    Filter on attributes needed on target node.
    """
    # TODO: support regex?
    rm = []
    for condition in conditions['attributes']:
        for candidate in candidate_list:
            for s, t in candidate:
                attrn = conditions['attributes'][condition][0]
                attrv = conditions['attributes'][condition][1]
                if s == condition and attrn not in container.node[t]:
                    rm.append(candidate)
                if s == condition and attrn in container.node[t] \
                        and attrv != container.node[t][attrn]:
                    rm.append(candidate)
    return rm


def _same_filter(n1, n2, candidate_list):
    """
    Filter out candidates which do not adhere the same target composition
    request.
    """
    rm = []
    for candidate in candidate_list:
        n1_trg = ''
        n2_trg = ''
        for s, t in candidate:
            if n1_trg == '' and s == n1:
                n1_trg = t
            elif n1_trg != '' and s == n2:
                if t != n1_trg:
                    rm.append(candidate)
            if n2_trg == '' and s == n2:
                n2_trg = t
            elif n2_trg != '' and s == n1:
                if t != n2_trg:
                    rm.append(candidate)
    return rm


def _diff_filter(n1, n2, candidate_list):
    """
    Filter out candidates which do not adhere the different target composition
    request.
    """
    rm = []
    for candidate in candidate_list:
        n1_trg = ''
        n2_trg = ''
        for s, t in candidate:
            if n1_trg == '' and s == n1:
                n1_trg = t
            elif n1_trg != '' and s == n2:
                if t == n1_trg:
                    rm.append(candidate)
            if n2_trg == '' and s == n2:
                n2_trg = t
            elif n2_trg != '' and s == n1:
                if t == n2_trg:
                    rm.append(candidate)
    return rm


def _share_attr(container, attrn, nlist, candidate_list):
    """
    Filter out candidates which do not adhere the request that all target nodes
    stitched to in the nlist share the same attribute value for a given
    attribute name.
    """
    rm = []
    for candidate in candidate_list:
        attrv = ''
        for s, t in candidate:
            if s in nlist and attrv == '':
                 attrv = container.node[t][attrn]
            elif s in nlist and container.node[t][attrn] != attrv:
                rm.append(candidate)
    return rm


class BaseStitcher(object):
    """
    Base stitcher with the function which need to be implemented.
    """

    def __init__(self, filename='data/stitch.json'):
        self.rels = json.load(open(filename, 'r'))

    def stitch(self, container, request, conditions=None, filter=filter):
        """
        Stitch a request graph into an existing graph container. Returns a set
        of possible options.

        :param container: A graph describing the existing container with
            ranks.
        :param request: A graph describing the request.
        :param conditions: Dictionary with conditions - e.g. node a & b need
            to be related to node c.
        :param filter: Function which allows for filtering useless options
            upfront.
        :return: The resulting graphs(s).
        """
        res = []
        # TODO: optimize this

        # 1. find possible mappings
        tmp = {}
        for node, attr in request.nodes(data=True):
            if attr['type'] in self.rels:
                candidates = self._find_nodes(container,
                                              self.rels[attr['type']])
                for candidate in candidates:
                    if node not in tmp:
                        tmp[node] = [candidate]
                    else:
                        tmp[node].append(candidate)

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

        # 3. (optional step): filter
        candidate_edge_list = filter(container, candidate_edge_list,
                                     conditions)

        # 4. create candidate containers
        tmp_graph = nx.union(container, request)
        for item in candidate_edge_list:
            candidate_graph = tmp_graph.copy()
            for s, t in item:
                candidate_graph.add_edge(s, t)
            res.append(candidate_graph)
        return res

    def validate(self, graphs):
        """
        Validate a set of graphs from the stitch() function. Return a
        dictionary with the index & explanatory text.

        :param graphs: List of possible graphs
        :return: dict with int:str.
        """
        # TODO: allow for chaining of validators & stitchers
        raise NotImplementedError('Needs to be implemented...')

    def _find_nodes(self, graph, tzpe):
        res = []
        for node, values in graph.nodes(data=True):
            if values['type'] == tzpe:
                res.append(node)
        return res


class IncomingEdgeStitcher(BaseStitcher):
    """
    Implemented simple rule to validate based on # of incoming edges.
    """

    def validate(self, graphs, condition={}):
        """
        In case a node of a certain type has more then a threshold of incoming
        edges determine a possible stitches as a bad stitch.
        """
        res = {}
        i = 0
        for candidate in graphs:
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


class NodeRankStitcher(BaseStitcher):
    """
    Implements simple rule to validate stitches based on ranks & incoming edges
    of a node.
    """

    def validate(self, graphs, condition={}):
        """
        In case a rank of a node and # of incoming edges increases determine
        possible stitches as a bad stitch.
        """
        res = {}
        i = 0
        for candidate in graphs:
            res[i] = 'ok'
            for node, values in candidate.nodes(data=True):
                if values['type'] not in condition.keys():
                    continue
                else:
                    tmp = condition[values['type']]
                if len(candidate.in_edges(node)) >= tmp[0] \
                        and values['rank'] >= tmp[1]:
                    res[i] = 'node ' + str(node) + ' has a high rank.'
            i += 1
        return res
