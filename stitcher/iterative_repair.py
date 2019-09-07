"""
Module using an iterative repair approach.
"""

import logging
import random
import re

import networkx as nx

import stitcher


def convert_conditions(conditions):
    """
    Convert the conditions to a mapping of nodename->list of conditions.
    """
    if conditions is None:
        return {}
    res = {}
    if 'attributes' in conditions:
        for condition in conditions['attributes']:
            cond = condition[0]
            node = condition[1][0]
            attr = condition[1][1]
            if node in res:
                res[node].append((cond, attr))
            else:
                res[node] = [(cond, attr)]
    if 'compositions' in conditions:
        for condition in conditions['compositions']:
            cond = condition[0]
            if cond in ['same', 'diff']:
                for item in condition[1]:
                    node = item
                    if node in res:
                        res[node].append((cond, [item for item in condition[1]
                                                 if item != node][0]))
                    else:
                        res[node] = [(cond, [item for item in condition[1]
                                             if item != node][0])]
            else:
                for item in condition[1][1]:
                    node = item
                    attr = condition[1][0]
                    if node in res:
                        res[node].append((cond, (attr, [item for item in
                                                        condition[1]
                                                        if item != node])))
                    else:
                        res[node] = [(cond, (attr, [item for item in
                                                    condition[1]
                                                    if item != node]))]
    return res


class IterativeRepairStitcher(stitcher.Stitcher):
    """
    Stitcher using a iterative repair approach to solve the constraints.
    """

    def __init__(self, max_steps=30, filename=None):
        super(IterativeRepairStitcher, self).__init__(filename=filename)
        self.steps = max_steps

    def stitch(self, container, request, conditions=None):
        conditions = convert_conditions(conditions)
        mapping = {}

        # initial (random mapping)
        for node, attr in request.nodes(data=True):
            mapping[node] = self._pick_random(container,
                                              attr[stitcher.TYPE_ATTR])
        logging.info('Initial random stitching: %s.', mapping)

        # start the solving process.
        res = self._solve(container, request, conditions, mapping)
        if res >= 0:
            logging.info('Found solution in %s iterations: %s.', res, mapping)
            tmp_graph = nx.union(container, request)
            for item in mapping:
                tmp_graph.add_edge(item, mapping[item])
            return [tmp_graph]
        logging.error('Could not find a solution in %s steps.', self.steps)
        return []

    def _solve(self, container, request, conditions, mapping):
        """
        The actual iterative repair algorithm.
        """
        for i in range(self.steps):
            logging.debug('Iteration: %s.', i)
            conflicts = self.find_conflicts(container, request, conditions,
                                            mapping)
            if not conflicts:
                return i
            logging.debug('Found %s conflict(s) in current stitch %s - %s',
                          len(conflicts), mapping, conflicts)
            conflict = self.next_conflict(conflicts)
            logging.debug('Will try to fix conflict: %s.', conflict)
            self.fix_conflict(conflict, container, request, mapping)
        return -1

    def find_conflicts(self, container, request, conditions, mapping):
        """
        Find the conflicts in a given mapping between request & container.

        Return None if no conflicts can be found.

        Overwrite this routine if you need additional conflict resolution
        mechanism - a sub optimal mapping (e.g. based on the rank) could also
        be seen as a conflict.
        """
        res = []
        for node in request.nodes():
            if node in conditions:
                for condy in conditions[node]:
                    tmp = _check_condition(node, condy, container, mapping)
                    if tmp:
                        res.append(tmp)
        return res

    def next_conflict(self, conflicts):
        """
        Given a set of conflicts pick the conflict to solve next.

        Overwrite this routine if you prefer another ordering than the
        default. For example based on a rank of a sub optimal mapping.
        """
        return random.choice(conflicts)

    def fix_conflict(self, conflict, container, request, mapping):
        """
        Fix a given conflict.

        Overwrite this routine with your own optimized fixer if needed.
        """
        # TODO: write solving routines for conditions that are available.
        tmp = self._pick_random(container,
                                request.node[conflict[0]][stitcher.TYPE_ATTR])
        mapping[conflict[0]] = tmp

    def _pick_random(self, container, req_node_type):
        """
        Randomly pick a node in container for a node in req.
        """
        i = 30
        while i >= 0:
            cand_name, attrs = random.choice(list(container.nodes(data=True)))
            if attrs[stitcher.TYPE_ATTR] == self.rels[req_node_type]:
                return cand_name
            i -= 1
        logging.warning('Checking if there is a node that matches...')
        for node, attr in container.nodes(data=True):
            if attr[stitcher.TYPE_ATTR] == self.rels[req_node_type]:
                return node
        raise Exception('No node in the container has the required type '
                        '%s.' % self.rels[req_node_type])


def _check_condition(node, condy, container, mapping):
    res = _check_attributes(node, condy, container, mapping)
    if not res:
        res = _check_compositions(node, condy, container, mapping)
    return res


def _check_attributes(node, condy, container, mapping):
    cond = condy[0]
    attrs = condy[1]
    # attributes
    if cond == 'eq':
        if attrs[0] not in container.node[mapping[node]] or \
                container.node[mapping[node]][attrs[0]] != attrs[1]:
            return node, condy
    elif cond == 'neq':
        if attrs[0] in container.node[mapping[node]] and \
                container.node[mapping[node]][attrs[0]] == attrs[1]:
            return node, condy
    elif cond == 'lt':
        if attrs[0] not in container.node[mapping[node]] or \
                container.node[mapping[node]][attrs[0]] > attrs[1]:
            return node, condy
    elif cond == 'gt':
        if attrs[0] not in container.node[mapping[node]] or \
                container.node[mapping[node]][attrs[0]] < attrs[1]:
            return node, condy
    elif cond == 'regex':
        if attrs[0] not in container.node[mapping[node]] or \
                not re.search(attrs[1],
                              container.node[mapping[node]][attrs[0]]):
            return node, condy
    return None


def _check_compositions(node, condy, container, mapping):
    cond = condy[0]
    attrs = condy[1]
    # compositions
    if cond == 'same':
        if mapping[node] != mapping[attrs]:
            return node, condy
    elif cond == 'diff':
        if mapping[node] == mapping[attrs]:
            return node, condy
    elif cond == 'share':
        attr_name = attrs[0]
        for ngbh in attrs[1]:
            if attr_name not in container.node[mapping[ngbh]] or \
                    container.node[mapping[ngbh]][attr_name] != \
                    container.node[mapping[node]][attr_name]:
                return node, condy
    elif cond == 'nshare':
        attr_name = attrs[0]
        for ngbh in attrs[1]:
            if attr_name not in container.node[mapping[ngbh]] or \
                    container.node[mapping[ngbh]][attr_name] == \
                    container.node[mapping[node]][attr_name]:
                return node, condy
    return None
