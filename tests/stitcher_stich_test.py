"""
Unittest for the basic stitcher.
"""

import json
import unittest
import sys

import networkx as nx

from networkx.readwrite import json_graph

from stitcher import stitch


class TestFilteringConditions(unittest.TestCase):
    """
    Tests the filter functions and validates that the right candidates are
    eliminated.
    """

    def setUp(self):
        self.container = nx.DiGraph()
        self.container.add_node('1', **{'type': 'a', 'foo': 'x', 'bar': 5,
                                        'retest': 'abcde'})
        self.container.add_node('2', **{'type': 'a', 'foo': 'y', 'bar': 7})
        self.container.add_node('3', **{'type': 'b', 'foo': 'x'})
        self.container.add_edge('1', '2')
        self.container.add_edge('2', '3')

        self.request = nx.DiGraph()
        self.request.add_node('a', **{'type': 'x'})
        self.request.add_node('b', **{'type': 'y'})
        self.request.add_edge('a', 'b')

        self.cut = stitch.GlobalStitcher()

    def assertItemsEqual(self, first, second):
        """
        Python2->3 fix...
        """
        if sys.version_info[0] >= 3:
            self.assertCountEqual(first, second)
        else:
            super(TestFilteringConditions, self).assertItemsEqual(first,
                                                                  second,
                                                                  'override.')

    def test_filter_for_sanity(self):
        """
        Test filter for sanity.
        """
        # none given as condition should results input = output
        inp = [1, 2, 3]
        out = stitch.my_filter(self.container, [1, 2, 3], None)
        self.assertEqual(inp, out)

        # node a requires target node to have attribute foo set to y
        condy = {'attributes': [('eq', ('a', ('foo', 'y')))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->2, b->3!
        self.assertEqual(len(res1), 1)
        self.assertItemsEqual([('1', '2'), ('a', 'b'), ('2', '3'), ('b', '3'),
                               ('a', '2')], res1[0].edges())

        # node a requires target node to have attribute foo set to 5
        condy = {'attributes': [('eq', ('a', ('bar', 5)))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->1, b->3!
        self.assertEqual(len(res1), 1)
        self.assertItemsEqual([('1', '2'), ('a', 'b'), ('2', '3'), ('b', '3'),
                               ('a', '1')], res1[0].edges())

        # node a requires target node to have attribute foo not set to y
        condy = {'attributes': [('neq', ('a', ('foo', 'y')))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->1, b->3!
        self.assertEqual(len(res1), 1)
        self.assertItemsEqual([('1', '2'), ('a', 'b'), ('2', '3'), ('b', '3'),
                               ('a', '1')], res1[0].edges())

        # node a requires target node to have attribute foo not set to 5
        condy = {'attributes': [('neq', ('a', ('bar', 5)))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->2, b->3!
        self.assertEqual(len(res1), 1)
        self.assertItemsEqual([('1', '2'), ('a', 'b'), ('2', '3'), ('b', '3'),
                               ('a', '2')], res1[0].edges())

        # node a requires target node to have an attribute bar with value > 5
        condy = {'attributes': [('lg', ('a', ('bar', 5)))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->2, b->3!
        self.assertEqual(len(res1), 1)
        self.assertItemsEqual([('1', '2'), ('a', 'b'), ('2', '3'), ('b', '3'),
                               ('a', '2')], res1[0].edges())

        # node a requires target node to have an attribute xyz with value > 5
        condy = {'attributes': [('lg', ('a', ('xyz', 5)))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # no stitch possible
        self.assertEqual(len(res1), 0)

        # node a requires target node to have an attribute bar with value < 6
        condy = {'attributes': [('lt', ('a', ('bar', 6)))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->1, b->3!
        self.assertEqual(len(res1), 1)
        self.assertItemsEqual([('1', '2'), ('a', 'b'), ('2', '3'), ('b', '3'),
                               ('a', '1')], res1[0].edges())

        # node a requires target node to have an attribute xyz with value < 5
        condy = {'attributes': [('lt', ('a', ('xyz', 5)))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # no stitch possible
        self.assertEqual(len(res1), 0)

        # node a requires target node to have an attribute retest which starts
        # with an 'a'
        condy = {'attributes': [('regex', ('a', ('retest', '^a')))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->1, b->3!
        self.assertEqual(len(res1), 1)
        self.assertItemsEqual([('1', '2'), ('a', 'b'), ('2', '3'), ('b', '3'),
                               ('a', '1')], res1[0].edges())

        # node a requires target node to have an attribute retest which starts
        # with an 'c'
        condy = {'attributes': [('regex', ('a', ('retest', '^c')))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # no options left.
        self.assertEqual(len(res1), 0)

        self.container.add_node('4', **{'type': 'b', 'foo': 'x'})
        self.container.add_edge('3', '4')
        self.request.add_node('c', **{'type': 'y'})
        self.request.add_edge('b', 'c')

        # node c & b to be stitched to same target!
        condy = {'compositions': [('same', ('b', 'c'))],
                 'attributes': [('eq', ('a', ('foo', 'x')))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        condy = {'compositions': [('same', ('c', 'b'))],
                 'attributes': [('eq', ('a', ('foo', 'x')))]}
        res2 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 2 options left: b&c->3 or b&c->4
        self.assertEqual(len(res1), 2)
        self.assertEqual(len(res2), 2)
        # should be identical.
        self.assertItemsEqual(res1[0].edges(), res2[0].edges())
        self.assertItemsEqual(res1[1].edges(), res2[1].edges())
        self.assertItemsEqual([('a', '1'), ('a', 'b'), ('b', 'c'), ('1', '2'),
                               ('3', '4'), ('2', '3'), ('b', '3'), ('c', '3')],
                              res1[0].edges())
        self.assertItemsEqual([('a', '1'), ('a', 'b'), ('b', 'c'), ('1', '2'),
                               ('3', '4'), ('2', '3'), ('b', '4'), ('c', '4')],
                              res1[1].edges())

        # node a & b to be stitched to different targets!
        condy = {'compositions': [('diff', ('b', 'c'))],
                 'attributes': [('eq', ('a', ('foo', 'x')))]}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        condy = {'compositions': [('diff', ('c', 'b'))],
                 'attributes': [('eq', ('a', ('foo', 'x')))]}
        res2 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 2 options left: b->3 & c->4 or b->4 & c->3
        self.assertEqual(len(res1), 2)
        self.assertEqual(len(res2), 2)
        # should be identical.
        self.assertItemsEqual(res1[0].edges(), res2[0].edges())
        self.assertItemsEqual(res1[1].edges(), res2[1].edges())
        either_called = False
        if ('b', '4') in res1[0].edges():
            self.assertItemsEqual([('a', '1'), ('a', 'b'), ('b', 'c'),
                                   ('1', '2'), ('3', '4'), ('2', '3'),
                                   ('b', '4'), ('c', '3')],
                                  res1[0].edges())
            self.assertItemsEqual([('a', '1'), ('a', 'b'), ('b', 'c'),
                                   ('1', '2'), ('3', '4'), ('2', '3'),
                                   ('b', '3'), ('c', '4')],
                                  res1[1].edges())
            either_called = True
        elif ('b', '4') in res1[1].edges():
            self.assertItemsEqual([('a', '1'), ('a', 'b'), ('b', 'c'),
                                   ('1', '2'), ('3', '4'), ('2', '3'),
                                   ('b', '4'), ('c', '3')],
                                  res1[1].edges())
            self.assertItemsEqual([('a', '1'), ('a', 'b'), ('b', 'c'),
                                   ('1', '2'), ('3', '4'), ('2', '3'),
                                   ('b', '3'), ('c', '4')],
                                  res1[0].edges())
            either_called = True
        self.assertTrue(either_called)

    def test_attr_sharing_filter_for_sanity(self):
        """
        Test filter for sanity with a more complex setup.
        """
        container = nx.DiGraph()
        container.add_node('a', **{'type': 'a', 'group': '1', 'geo': 'eu'})
        container.add_node('b', **{'type': 'b', 'group': '1', 'geo': 'us'})
        container.add_node('c', **{'type': 'a', 'group': '2'})
        container.add_node('d', **{'type': 'b', 'group': '2'})
        container.add_node('e', **{'type': 'b'})
        container.add_edge('a', 'b')
        container.add_edge('b', 'c')
        container.add_edge('c', 'd')

        request = nx.DiGraph()
        request.add_node('1', **{'type': 'x'})
        request.add_node('2', **{'type': 'y'})
        request.add_node('3', **{'type': 'y'})
        request.add_edge('1', '2')
        request.add_edge('1', '3')

        condy = {'compositions': [('share', ('group', ['1', '2'])),
                                  ('same', ('2', '3'))],
                 'attributes': [('eq', ('1', ('geo', 'eu')))]}
        res1 = self.cut.stitch(container, request, conditions=condy)

        # only one option possible
        self.assertEqual(len(res1), 1)
        # verify stitches
        self.assertIn(('1', 'a'), res1[0].edges())
        self.assertIn(('2', 'b'), res1[0].edges())
        self.assertIn(('3', 'b'), res1[0].edges())

        condy = {'compositions': [('nshare', ('group', ['2', '3']))],
                 'attributes': [('eq', ('1', ('geo', 'eu'))),
                                ('eq', ('2', ('geo', 'us')))]}
        res1 = self.cut.stitch(container, request, conditions=condy)

        # only one option possible
        self.assertEqual(len(res1), 1)
        # verify stitches
        self.assertIn(('1', 'a'), res1[0].edges())
        self.assertIn(('2', 'b'), res1[0].edges())
        self.assertIn(('3', 'd'), res1[0].edges())


class TestGlobalStitcher(unittest.TestCase):
    """
    Test the global stitcher class.
    """

    def setUp(self):
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = stitch.GlobalStitcher()

    def test_stitch_for_success(self):
        """
        Test stitch for success.
        """
        self.cut.stitch(self.container, self.request)

    def test_stitch_for_sanity(self):
        """
        Test stitch for sanity.
        """
        # basic stitch test
        res1 = self.cut.stitch(self.container, self.request)
        self.assertTrue(len(res1) > 0)
        self.assertEqual(res1[0].number_of_edges(),
                         self.container.number_of_edges() + 5)
        self.assertEqual(res1[0].number_of_nodes(),
                         self.container.number_of_nodes() + 3)

        # let's add a node to the request which does not require to be
        # stitched to the container. Hence added edges = 3!
        self.request.add_node('n', **{'type': 'foo', 'rank': 7})
        self.request.add_edge('k', 'n')
        self.request.add_edge('n', 'l')

        self.assertTrue(len(res1) > 0)
        self.assertEqual(res1[0].number_of_edges(),
                         self.container.number_of_edges() + 5)
        self.assertEqual(res1[0].number_of_nodes(),
                         self.container.number_of_nodes() + 3)
