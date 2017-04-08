"""
Implements stitching, validation and filtering functions.
"""

import copy
import itertools
import re

import networkx as nx

import stitcher


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
    Default filter which scans the candidate edges and eliminates those
    candidates which do not adhere the conditions. Following conditions are
    available:

    attributes - the target node e.g. needs to have a certain attribute
    composition - two nodes need to e.g. have same/different/shared attributes
        for the target nodes.

    :param edge_list: the candidate edge list as created by stitch().
    :param conditions: dictionary containing the conditions.
    :return: The filtered dict with possible edges.
    """
    if conditions is None:
        return edge_list
    else:
        if 'attributes' in conditions:
            for condition in conditions['attributes']:
                cond = condition[0]
                para1 = condition[1][0]
                para2 = condition[1][1]
                if cond == 'eq':
                    _eq_attr_filter(container, para1, para2, edge_list)
                elif cond == 'neq':
                    _neq_attr_filter(container, para1, para2, edge_list)
                elif cond == 'lg':
                    _lg_attr_filter(container, para1, para2, edge_list)
                elif cond == 'lt':
                    _lt_attr_filter(container, para1, para2, edge_list)
                elif cond == 'regex':
                    _regex_attr_filter(container, para1, para2, edge_list)
        if 'compositions' in conditions:
            for condition in conditions['compositions']:
                cond = condition[0]
                para1 = condition[1][0]
                para2 = condition[1][1]
                if cond == 'same':
                    _same_filter(para1, para2, edge_list)
                elif cond == 'diff':
                    _diff_filter(para1, para2, edge_list)
                elif cond == 'share':
                    _share_attr(container, para1, para2, edge_list)
                elif cond == 'nshare':
                    _nshare_attr(container, para1, para2, edge_list)
        return edge_list


def _eq_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes needed on target node.
    """
    for candidate in list(candidate_list.keys()):
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate_list[candidate]:
            if src == node and attrn not in container.node[trg]:
                candidate_list.pop(candidate)
                break
            if src == node and attrn in container.node[trg] \
                    and attrv != container.node[trg][attrn]:
                candidate_list.pop(candidate)
                break


def _neq_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes unequal to requested value.
    """
    for candidate in list(candidate_list.keys()):
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate_list[candidate]:
            if src == node and attrn in container.node[trg] \
                    and attrv == container.node[trg][attrn]:
                candidate_list.pop(candidate)
                break


def _lg_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes larger than requested value.
    """
    for candidate in list(candidate_list.keys()):
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate_list[candidate]:
            if src == node and attrn not in container.node[trg]:
                candidate_list.pop(candidate)
                break
            if src == node and attrn in container.node[trg] \
                    and container.node[trg][attrn] <= attrv:
                candidate_list.pop(candidate)
                break


def _lt_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes less than requested value.
    """
    for candidate in list(candidate_list.keys()):
        attrn = condition[0]
        attrv = condition[1]
        for src, trg in candidate_list[candidate]:
            if src == node and attrn not in container.node[trg]:
                candidate_list.pop(candidate)
                break
            if src == node and attrn in container.node[trg] \
                    and attrv < container.node[trg][attrn]:
                candidate_list.pop(candidate)
                break


def _regex_attr_filter(container, node, condition, candidate_list):
    """
    Filter on attributes which match an regex.
    """
    for candidate in list(candidate_list.keys()):
        attrn = condition[0]
        regex = condition[1]
        for src, trg in candidate_list[candidate]:
            if src == node and attrn not in container.node[trg]:
                candidate_list.pop(candidate)
                break
            if src == node and attrn in container.node[trg] \
                    and not re.search(regex, container.node[trg][attrn]):
                candidate_list.pop(candidate)
                break


def _same_filter(node1, node2, candidate_list):
    """
    Filter out candidates which do not adhere the same target composition
    request.
    """
    for candidate in list(candidate_list.keys()):
        n1_trg = ''
        n2_trg = ''
        for src, trg in candidate_list[candidate]:
            if n1_trg == '' and src == node1:
                n1_trg = trg
            elif n1_trg != '' and src == node2:
                if trg != n1_trg:
                    candidate_list.pop(candidate)
                    break
            if n2_trg == '' and src == node2:
                n2_trg = trg
            elif n2_trg != '' and src == node1:
                if trg != n2_trg:
                    candidate_list.pop(candidate)
                    break


def _diff_filter(node1, node2, candidate_list):
    """
    Filter out candidates which do not adhere the different target composition
    request.
    """
    for candidate in list(candidate_list.keys()):
        n1_trg = ''
        n2_trg = ''
        for src, trg in candidate_list[candidate]:
            if n1_trg == '' and src == node1:
                n1_trg = trg
            elif n1_trg != '' and src == node2:
                if trg == n1_trg:
                    candidate_list.pop(candidate)
                    break
            if n2_trg == '' and src == node2:
                n2_trg = trg
            elif n2_trg != '' and src == node1:
                if trg == n2_trg:
                    candidate_list.pop(candidate)
                    break


def _share_attr(container, attrn, nlist, candidate_list):
    """
    Filter out candidates which do not adhere the request that all target nodes
    stitched to in the nlist share the same attribute value for a given
    attribute name.
    """
    for candidate in list(candidate_list.keys()):
        attrv = ''
        for src, trg in candidate_list[candidate]:
            if attrn not in container.node[trg]:
                candidate_list.pop(candidate)
                break
            elif src in nlist and attrv == '':
                attrv = container.node[trg][attrn]
            elif src in nlist and container.node[trg][attrn] != attrv:
                candidate_list.pop(candidate)
                break


def _nshare_attr(container, attrn, nlist, candidate_list):
    """
    Filter out candidates which do not adhere the request that all target nodes
    stitched to in the nlist do not share the same attribute value for a given
    attribute name.
    """
    for candidate in list(candidate_list.keys()):
        attrv = ''
        for src, trg in candidate_list[candidate]:
            if attrn not in container.node[trg]:
                candidate_list.pop(candidate)
                break
            elif src in nlist and attrv == '':
                attrv = container.node[trg][attrn]
            elif src in nlist and container.node[trg][attrn] == attrv:
                candidate_list.pop(candidate)
                break


class GlobalStitcher(stitcher.Stitcher):
    """
    Base stitcher with the functions which need to be implemented.
    """

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
        # TODO: optimize this using concurrency & parallelism

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
        # dictionary so we have hashed keys (--> speed)
        candidate_edges = {}
        keys = list(tmp.keys())
        per = [tmp[key] for key in keys]

        for edge_list in itertools.product(*per):
            j = 0
            edges = []
            for item in edge_list:
                edges.append((keys[j], item))
                j += 1
            if len(edges) > 0:
                candidate_edges[str(edges)] = edges

        # 3. (optional step): filter
        candidate_edges = candidate_filter(container, candidate_edges,
                                           conditions)

        # 4. create candidate containers
        tmp_graph = nx.union(container, request)
        for item in candidate_edges.values():
            candidate_graph = copy.deepcopy(tmp_graph)  # faster graph copy
            # candidate_graph = tmp_graph.copy()
            for src, trg in item:
                candidate_graph.add_edge(src, trg)
            res.append(candidate_graph)
        return res
