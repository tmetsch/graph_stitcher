
"""
Implements stitching, validation and filtering functions.
"""

import itertools
import json
import re

import networkx as nx


def _find_nodes(graph, tzpe):
    """
    Find nodes of a certain type in a graph.
    """
    res = []
    for node, values in graph.nodes(data=True):
        if values['type'] == tzpe:
            res.append(node)
    return res


def my_filter(container, edge_list, conditions):
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
        rm_list = []
        if 'attributes' in conditions:
            for condition in conditions['attributes']:
                cond = condition[0]
                para1 = condition[1][0]
                para2 = condition[1][1]
                if cond is 'eq':
                    rm_list.extend(_eq_attr_filter(container, para1, para2,
                                                   edge_list))
                if cond is 'neq':
                    rm_list.extend(_neq_attr_filter(container, para1, para2,
                                                    edge_list))
                if cond is 'lg':
                    rm_list.extend(_lg_attr_filter(container, para1, para2,
                                                   edge_list))
                if cond is 'lt':
                    rm_list.extend(_lt_attr_filter(container, para1, para2,
                                                   edge_list))
                if cond is 'regex':
                    rm_list.extend(_regex_attr_filter(container, para1, para2,
                                                      edge_list))
        if 'compositions' in conditions:
            for condition in conditions['compositions']:
                cond = condition[0]
                para1 = condition[1][0]
                para2 = condition[1][1]
                if cond is 'same':
                    rm_list.extend(_same_filter(para1, para2, edge_list))
                if cond is 'diff':
                    rm_list.extend(_diff_filter(para1, para2, edge_list))
                if cond is 'share':
                    rm_list.extend(_share_attr(container, para1, para2,
                                               edge_list))
        for item in rm_list:
            try:
                edge_list.remove(item)
            except ValueError:
                pass   # multiple filters might request removal.
        return edge_list


def _eq_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes needed on target node.
    """
    res = []
    for candidate in candidate_list:
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate:
            if src == node and attrn not in container.node[trg]:
                res.append(candidate)
            if src == node and attrn in container.node[trg] \
                    and attrv != container.node[trg][attrn]:
                res.append(candidate)
    return res


def _neq_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes unequal to requested value.
    """
    res = []
    for candidate in candidate_list:
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate:
            if src == node and attrn in container.node[trg] \
                    and attrv == container.node[trg][attrn]:
                res.append(candidate)
    return res


def _lg_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes larger than requested value.
    """
    res = []
    for candidate in candidate_list:
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate:
            if src == node and attrn not in container.node[trg]:
                res.append(candidate)
            if src == node and attrn in container.node[trg] \
                    and attrv > container.node[trg][attrn]:
                res.append(candidate)
    return res


def _lt_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes less than requested value.
    """
    res = []
    for candidate in candidate_list:
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate:
            if src == node and attrn not in container.node[trg]:
                res.append(candidate)
            if src == node and attrn in container.node[trg] \
                    and attrv < container.node[trg][attrn]:
                res.append(candidate)
    return res


def _regex_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes which match an regex.
    """
    res = []
    for candidate in candidate_list:
        attrn = condition[0]
        regex = condition[1]
        for src, trg in candidate:
            if src == node and attrn not in container.node[trg]:
                res.append(candidate)
            if src == node and attrn in container.node[trg] \
                    and not re.search(regex, container.node[trg][attrn]):
                res.append(candidate)
    return res


def _same_filter(node1, node2, candidate_list):
    """
    Filter out candidates which do not adhere the same target composition
    request.
    """
    res = []
    for candidate in candidate_list:
        n1_trg = ''
        n2_trg = ''
        for src, trg in candidate:
            if n1_trg == '' and src == node1:
                n1_trg = trg
            elif n1_trg != '' and src == node2:
                if trg != n1_trg:
                    res.append(candidate)
            if n2_trg == '' and src == node2:
                n2_trg = trg
            elif n2_trg != '' and src == node1:
                if trg != n2_trg:
                    res.append(candidate)
    return res


def _diff_filter(node1, node2, candidate_list):
    """
    Filter out candidates which do not adhere the different target composition
    request.
    """
    res = []
    for candidate in candidate_list:
        n1_trg = ''
        n2_trg = ''
        for src, trg in candidate:
            if n1_trg == '' and src == node1:
                n1_trg = trg
            elif n1_trg != '' and src == node2:
                if trg == n1_trg:
                    res.append(candidate)
            if n2_trg == '' and src == node2:
                n2_trg = trg
            elif n2_trg != '' and src == node1:
                if trg == n2_trg:
                    res.append(candidate)
    return res


def _share_attr(container, attrn, nlist, candidate_list):
    """
    Filter out candidates which do not adhere the request that all target nodes
    stitched to in the nlist share the same attribute value for a given
    attribute name.
    """
    res = []
    for candidate in candidate_list:
        attrv = ''
        for src, trg in candidate:
            if attrn not in container.node[trg]:
                res.append(candidate)
            elif src in nlist and attrv == '':
                attrv = container.node[trg][attrn]
            elif src in nlist and container.node[trg][attrn] != attrv:
                res.append(candidate)
    return res


class BaseStitcher(object):
    """
    Base stitcher with the function which need to be implemented.
    """

    def __init__(self, filename='data/stitch.json'):
        self.rels = json.load(open(filename, 'r'))

    def stitch(self, container, request, conditions=None,
               candidate_filter=my_filter):
        """
        Stitch a request graph into an existing graph container. Returns a set
        of possible options.

        :param container: A graph describing the existing container with
            ranks.
        :param request: A graph describing the request.
        :param conditions: Dictionary with conditions - e.g. node a & b need
            to be related to node c.
        :param candidate_filter: Function which allows for filtering useless
            options upfront.
        :return: The resulting graphs(s).
        """
        res = []
        # TODO: optimize this

        # 1. find possible mappings
        tmp = {}
        for node, attr in request.nodes(data=True):
            if attr['type'] in self.rels:
                candidates = _find_nodes(container, self.rels[attr['type']])
                for candidate in candidates:
                    if node not in tmp:
                        tmp[node] = [candidate]
                    else:
                        tmp[node].append(candidate)

        # 2. find candidates
        candidate_edge_list = []
        keys = tmp.keys()
        per = []
        for key in keys:
            per.append(tmp[key])

        for edge_list in itertools.product(*per):
            j = 0
            edges = []
            for item in edge_list:
                edges.append((keys[j], item))
                j += 1
            candidate_edge_list.append(edges)

        # 3. (optional step): filter
        candidate_edge_list = candidate_filter(container, candidate_edge_list,
                                               conditions)

        # 4. create candidate containers
        tmp_graph = nx.union(container, request)
        for item in candidate_edge_list:
            candidate_graph = tmp_graph.copy()
            for src, trg in item:
                candidate_graph.add_edge(src, trg)
            res.append(candidate_graph)
        return res

    def validate(self, graphs):
        """
        Validate a set of graphs from the stitch() function. Return a
        dictionary with the index & explanatory text.

        :param graphs: List of possible graphs
        :return: dict with int:str.
        """
        # XXX: allow for chaining of validators & stitchers
        raise NotImplementedError('Needs to be implemented...')


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
