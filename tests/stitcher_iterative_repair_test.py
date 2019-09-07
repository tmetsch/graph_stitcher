"""
Unittests for iterative_repair module.
"""

import json
import unittest

import networkx as nx

from networkx.readwrite import json_graph

from stitcher import iterative_repair


def _sample_data():
    cont = nx.DiGraph()
    cont.add_node('1', **{'type': 'a', 'group': 'foo', 'rank': 1.0})
    cont.add_node('2', **{'type': 'b', 'group': 'foo', 'rank': 1.0})
    cont.add_node('3', **{'type': 'b', 'group': 'bar', 'rank': 2.0})
    cont.add_node('4', **{'type': 'a', 'group': 'bar', 'rank': 2.0})
    cont.add_edge('1', '2')
    cont.add_edge('2', '3')
    cont.add_edge('4', '3')

    req = nx.DiGraph()
    req.add_node('a', **{'type': 'x'})
    req.add_node('b', **{'type': 'y'})
    req.add_edge('a', 'b')
    return cont, req


class IterativeRepairStitcherTest(unittest.TestCase):
    """
    Test for class IterativeRepairStitcher.
    """

    def setUp(self) -> None:
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = iterative_repair.IterativeRepairStitcher()

    # Test for success.

    def test_stitch_for_success(self):
        """
        Test fo success.
        """
        self.cut.stitch(self.container, self.request)

    def test_find_conflicts_for_success(self):
        """
        Test for success.
        """
        cont, req = _sample_data()
        condy = {'attributes': [('eq', ('a', ('foo', 'bar')))]}
        self.cut.find_conflicts(cont, req, condy, {'a': '1'})

    def test_next_conflict_for_success(self):
        """
        Test for success.
        """
        self.cut.next_conflict([('foo', 'bar'), ('bar', 'foo')])

    def test_fix_for_success(self):
        """
        Test for success.
        """
        self.cut.fix_conflict(('k', ('eq', ('rank', 5))),
                              self.container,
                              self.request,
                              {'k': 'A'})

    # Test for failure.

    def test_stitch_for_failure(self):
        """
        Test for failure.
        """
        cont = nx.DiGraph()
        cont.add_node('foo', **{'type': 'a'})

        req = nx.DiGraph()
        req.add_node('bar', **{'type': 'y'})  # no matching type in container.

        self.assertRaises(Exception, self.cut.stitch, cont, req)

        # test with unsolvable case.
        cont, req = _sample_data()
        res = self.cut.stitch(cont, req, {
            'attributes':
                [('eq', ('a', ('buuha', 'asdf')))]
        })
        self.assertTrue(len(res) == 0)

    # Test for sanity.

    def test_stitch_for_sanity(self):
        """
        Test for sanity.
        """
        condy = {
            'attributes': [('eq', ('k', ('rank', 5)))]
        }
        res = self.cut.stitch(self.container, self.request, conditions=condy)

        # TODO: test with multigraph request!
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], nx.DiGraph)

    def test_find_conflicts_for_sanity(self):
        """
        Test for sanity.
        """
        cont, req = _sample_data()

        # a doesn't have foo attr.
        condy = {'a': [('eq', ('foo', 'bar'))]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a is in group foo
        condy = {'a': [('neq', ('group', 'foo'))]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a's rank is 1.0
        condy = {'a': [('lt', ('rank', 0.5))]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a's rank is 1.0
        condy = {'a': [('gt', ('rank', 2.0))]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a's group name is a word
        condy = {'a': [('regex', ('group', '\\d'))]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a & b not on same node...
        condy = {'a': [('same', 'b')], 'b': [('same', 'a')]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1', 'b': '2'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a & b not on same node...
        condy = {'a': [('diff', 'b')], 'b': [('diff', 'a')]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1', 'b': '1'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a & b not in same group
        condy = {'a': [('share', ('group', ['b']))],
                 'b': [('share', ('group', ['a']))]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1', 'b': '3'})
        self.assertEqual(condy['a'][0], res[0][1])
        # a & b in same group
        condy = {'a': [('nshare', ('group', ['b']))],
                 'b': [('nshare', ('group', ['a']))]}
        res = self.cut.find_conflicts(cont, req, condy, {'a': '1', 'b': '2'})
        self.assertEqual(condy['a'][0], res[0][1])

    def test_next_conflict_for_sanity(self):
        """
        Test for sanity.
        """
        res = self.cut.next_conflict(['foo', 'bar'])
        self.assertIsNotNone(res)

    def test_fix_for_sanity(self):
        """
        Test for sanity.
        """
        cont, req = _sample_data()
        mapping = {'a': '1'}
        self.cut.fix_conflict(('a', ('eq', ('foo', 'bar'))), cont, req,
                              mapping)
        self.assertIn('a', mapping)


class TestConvertConditions(unittest.TestCase):
    """
    Test the condition converter.
    """

    def setUp(self) -> None:
        self.cond = {
            'attributes': [('eq', ('a', ('foo', 'y'))),
                           ('neq', ('a', ('foo', 5))),
                           ('lt', ('a', ('foo', 4))),
                           ('lg', ('a', ('foo', 7))),
                           ('regex', ('a', ('foo', '^a')))],
            'compositions': [('same', ('1', '2')),
                             ('diff', ('3', '4')),
                             ('diff', ('3', '1')),
                             ('share', ('group', ['x', 'y'])),
                             ('nshare', ('group', ['a', 'b']))]
        }

    # Test for success.

    def test_convert_for_success(self):
        """
        Test for success.
        """
        iterative_repair.convert_conditions(self.cond)

    # Test for failure

    # N/A

    # Test for sanity.

    def test_convert_for_sanity(self):
        """
        Test for sanity.
        """
        res = iterative_repair.convert_conditions(self.cond)
        self.assertIn('a', res)
        self.assertIn('b', res)
        self.assertIn('x', res)
        self.assertIn('y', res)
        self.assertIn('1', res)
        self.assertIn('2', res)
        self.assertIn('3', res)
        self.assertIn('4', res)
        self.assertTrue(len(res['a']) == 6)  # eq, neq, lt, lg, regex, nshare
        self.assertTrue(len(res['b']) == 1)  # nshare
        self.assertTrue(len(res['x']) == 1)  # share
        self.assertTrue(len(res['y']) == 1)  # share
        self.assertTrue(len(res['1']) == 2)  # same, diff
        self.assertTrue(len(res['2']) == 1)  # same
        self.assertTrue(len(res['3']) == 2)  # 2x diff
        self.assertTrue(len(res['4']) == 1)  # diff
