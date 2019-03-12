"""
Unittest for the bidding module.
"""

import logging
import unittest

import networkx as nx

from stitcher import bidding

FORMAT = "%(asctime)s - %(filename)s - %(lineno)s - " \
         "%(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


class EntityTest(unittest.TestCase):
    """
    Testcase for the Entity class.
    """

    def setUp(self):
        self.map = {'type_a': 'type_x',
                    'type_b': 'type_y'}

        self.request = nx.DiGraph()
        self.request.add_node('a', **{'type': 'type_a'})
        self.request.add_node('b', **{'type': 'type_b'})
        self.request.add_node('c', **{'type': 'type_b'})
        self.request.add_edge('a', 'b')
        self.request.add_edge('b', 'c')

        self.container = nx.DiGraph()
        self.x_attr = {'type': 'type_x',
                       'foo': 3,
                       'group_1': 'group_a',
                       'group_2': 'group_b'}
        self.y_attr = {'type': 'type_y',
                       'foo': 5,
                       'group_1': 'group_a',
                       'group_2': 'group_c'}

    def test_trigger_for_success(self):
        """
        Test trigger for success.
        """
        cut = bidding.Entity('x', self.map, self.request, self.container)
        self.container.add_node(cut, **self.x_attr)
        cut.trigger({'assigned': {}, 'bids': []}, 'init')

    def test_trigger_for_failure(self):
        """
        Test trigger for failure.
        """
        pass

    def test_trigger_for_sanity(self):
        """
        Test trigger for failure.
        """
        # test calculation of credits to bid.
        # no conditions
        cut = bidding.Entity('x', self.map, self.request, self.container)
        self.container.add_node(cut, **self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': {}}, 'init')
        self.assertEqual(res['a'][1], 1.0)  # 1 because type matches.
        self.assertNotIn('b', bids)  # a should not bid on b.

        # lg
        self.container = nx.DiGraph()
        condy = {'attributes': [('lg', ('a', ('foo', 1)))]}
        cut = bidding.Entity('x', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertEqual(res['a'][1], 3.0)  # rank 3 - rank 1 + 1 for type = 2

        # lt
        self.container = nx.DiGraph()
        condy = {'attributes': [('lt', ('a', ('foo', 9)))]}
        cut = bidding.Entity('x', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertEqual(res['a'][1], 7.0)  # 9-3+1=7

        # eq
        self.container = nx.DiGraph()
        condy = {'attributes': [('eq', ('a', ('foo', 2)))]}
        cut = bidding.Entity('x', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.x_attr)
        res, _ = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertNotIn('a', bids)  # popped because not equal.

        # neq
        self.container = nx.DiGraph()
        condy = {'attributes': [('neq', ('a', ('group_1', 'group_a')))]}
        cut = bidding.Entity('x', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.x_attr)
        res, _ = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertNotIn('a', bids)  # popped because equal.

        # regex
        self.container = nx.DiGraph()
        condy = {'attributes': [('regex', ('a', ('group_1', '^z')))]}
        cut = bidding.Entity('x', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.x_attr)
        res, _ = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertNotIn('a', bids)  # popped because z not in group name.

        # same
        # 1. nothing assigned -> increase bit for both (50%)
        self.container = nx.DiGraph()
        condy = {'compositions': [('same', ['b', 'c'])]}
        cut = bidding.Entity('y', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.y_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertEqual(res['b'][1], 1.5)  # 1 + 0.5 increase
        self.assertEqual(res['c'][1], 1.5)  # 1 + 0.5 increase

        # 1. nothing assigned -> increase bit for both (50%)
        self.container = nx.DiGraph()
        condy = {'compositions': [('same', ['a', 'c'])]}
        cut = bidding.Entity('y', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.y_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertTrue('a' not in bids['y'])  # not bid on a
        self.assertTrue('c' not in bids['y'])  # not bid on c

        # 2. a,b, assigned to sth else -> nothing
        # so e.g. only better attribute matches can increase the need for it
        # to bid higher - and eventually stuff getting assigned here.

        # diff
        # 1. nothing assigned -> drop one bid
        self.container = nx.DiGraph()
        condy = {'compositions': [('diff', ['b', 'c'])]}
        cut = bidding.Entity('y', self.map, self.request, self.container,
                             condy)
        self.container.add_node(cut, **self.y_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        if 'c' in res:
            self.assertNotIn('b', bids['y'])  # drop other bid.
        elif 'b' in res:
            self.assertNotIn('c', bids['y'])  # drop other bid.

        # 2. a assigned, b no bid -> increase bid for b (50%)
        self.container = nx.DiGraph()
        condy = {'compositions': [('diff', ['a', 'c'])]}
        cut_x = bidding.Entity('x', self.map, self.request, self.container,
                               condy)
        cut_y = bidding.Entity('y', self.map, self.request, self.container,
                               condy)
        self.container.add_node(cut_x, **self.x_attr)
        self.container.add_node(cut_y, **self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        res, bids = cut_x.trigger({'assigned': {},
                                   'bids': []}, 'init')
        self.assertEqual(res['a'][0], 'x')
        self.assertEqual(res['c'][0], 'y')
        self.assertEqual(res['c'][1], 1.5)  # 1 (type) + 0.5 increase

        # 3. a,b, assigned to sth else -> if neighbour bids too -
        # increase bid a bit (25%)
        self.container = nx.DiGraph()
        condy = {'compositions': [('diff', ['a', 'c'])]}
        cut_x = bidding.Entity('x', self.map, self.request, self.container,
                               condy)
        cut_y = bidding.Entity('y', self.map, self.request, self.container,
                               condy)
        self.container.add_node(cut_x, **self.x_attr)
        self.container.add_node(cut_y, **self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        res, bids = cut_x.trigger({'assigned': {'a': ('k', 10.0),
                                                'c': ('l', 10.0)},
                                   'bids': []}, 'init')
        self.assertEqual(bids['y']['c'], 1.25)  # y bid on c + 0.25
        self.assertEqual(bids['x']['a'], 1.25)  # x bid on a + 0.25

        # share
        # 1. a assigned to x, I share attr with x -> increase bid (50%)
        self.container = nx.DiGraph()
        condy = {'compositions': [('share', ('group_1', ['a', 'b']))]}
        cut_x = bidding.Entity('x', self.map, self.request, self.container,
                               condy)
        cut_y = bidding.Entity('y', self.map, self.request, self.container,
                               condy)
        self.container.add_node(cut_x, **self.x_attr)
        self.container.add_node(cut_y, **self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        res, bids = cut_x.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertEqual(res['b'][1], 1.5)  # +50% b/c group complete.
        self.assertEqual(res['b'][0], 'y')  # b should be stitched to y
        self.assertEqual(res['a'][1], 1.5)  # +50% b/c group complete.
        self.assertEqual(res['a'][0], 'x')  # a should be stitched to x

        # nshare
        # 1. a assigned, b no bid -> increase bid for b (50%)
        self.container = nx.DiGraph()
        condy = {'compositions': [('nshare', ('group_2', ['a', 'b']))]}
        cut_x = bidding.Entity('x', self.map, self.request, self.container,
                               condy)
        cut_y = bidding.Entity('y', self.map, self.request, self.container,
                               condy)
        self.container.add_node(cut_x, **self.x_attr)
        self.container.add_node(cut_y, **self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        self.container.add_node(cut, **self.x_attr)
        res, bids = cut_x.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertEqual(res['b'][1], 1.5)  # 1 + 0.5 increase
        self.assertEqual(res['b'][0], 'y')  # b should be stitched to y
        self.assertEqual(res['a'][1], 1.0)  # a sits fine on x
        self.assertEqual(res['a'][0], 'x')  # a should be stitched to x


class BiddingStitcherTest(unittest.TestCase):
    """
    Testcase for the BiddingStitcher class.
    """

    def setUp(self):
        self.cut = bidding.BiddingStitcher()
        self.cut.rels = {'type_x': 'type_a',
                         'type_y': 'type_b',
                         'type_z': 'type_c'}

        self.container = nx.DiGraph()
        self.container.add_node('A', **{'type': 'type_a'})
        self.container.add_node('B', **{'type': 'type_b'})
        self.container.add_node('C', **{'type': 'type_c'})
        self.container.add_edge('A', 'B')
        self.container.add_edge('B', 'C')

        self.request = nx.DiGraph()
        self.request.add_node('X', **{'type': 'type_x'})
        self.request.add_node('Y', **{'type': 'type_y'})
        self.request.add_node('Z', **{'type': 'type_y'})
        self.request.add_edge('X', 'Y')
        self.request.add_edge('Y', 'Z')

    def test_stitch_for_success(self):
        """
        Test stitching for success.
        """
        self.cut.stitch(self.container, self.request)

    def test_stitch_for_sanity(self):
        """
        Test stitching for sanity
        """
        # shouldn't matter were we start
        for node in self.container.nodes():
            res = self.cut.stitch(self.container, self.request, start=node)
            self.assertIn(('X', 'A'), res[0].edges())
            self.assertIn(('Y', 'B'), res[0].edges())
            self.assertIn(('Z', 'B'), res[0].edges())

        # cycles shouldn't matter either
        self.container.add_edge('C', 'A')  # CYCLE!
        res = self.cut.stitch(self.container, self.request)
        self.assertIn(('X', 'A'), res[0].edges())
        self.assertIn(('Y', 'B'), res[0].edges())
        self.assertIn(('Z', 'B'), res[0].edges())

        # complex test with two groups.
        container = nx.DiGraph()
        container.add_node('A', **{'type': 'type_a', 'group': 'a', 'rank': 2})
        container.add_node('B', **{'type': 'type_b', 'group': 'a', 'rank': 3})
        container.add_node('I', **{'type': 'type_b', 'rank': 1})
        # XXX: 'group': 'c' is incomplete should only works because I uplevel
        # complete groups.
        container.add_node('J', **{'type': 'type_b', 'group': 'c', 'rank': 2})
        container.add_node('X', **{'type': 'type_b', 'group': 'b', 'rank': 2})
        container.add_node('Y', **{'type': 'type_a', 'group': 'b', 'rank': 5})
        container.add_edge('A', 'B')
        container.add_edge('B', 'I')
        container.add_edge('I', 'J')
        container.add_edge('J', 'X')
        container.add_edge('X', 'Y')

        request = nx.DiGraph()
        request.add_node('1', **{'type': 'type_x'})
        request.add_node('2', **{'type': 'type_y'})
        request.add_edge('1', '2')

        condy = {
            'compositions': [('share', ('group', ['1', '2']))],
            'attributes': [('lg', ('1', ('rank', 2))),
                           ('lg', ('2', ('rank', 2)))]
        }
        for node in container.nodes():
            res = self.cut.stitch(container, request, conditions=condy,
                                  start=node)
            self.assertIn(('1', 'Y'), res[0].edges())
            self.assertIn(('2', 'X'), res[0].edges())
