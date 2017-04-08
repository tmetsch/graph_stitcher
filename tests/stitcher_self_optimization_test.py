"""
Unittest for the self_optimization module.
"""


import logging
import unittest

import networkx as nx

from stitcher import self_optimization as so

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
        self.request.add_node('a', {'type': 'type_a'})
        self.request.add_node('b', {'type': 'type_b'})
        self.request.add_node('c', {'type': 'type_b'})
        self.request.add_edge('a', 'b')
        self.request.add_edge('b', 'c')

        self.container = nx.DiGraph()
        self.x_attr = {'type': 'type_x',
                       'foo': 3,
                       'group_1': 'a',
                       'group_2': 'b'}
        self.y_attr = {'type': 'type_y',
                       'foo': 5,
                       'group_1': 'a',
                       'group_2': 'c'}

    def test_trigger_for_success(self):
        """
        Test trigger for success.
        """
        cut = so.Entity('x', self.map, self.request, self.container)
        self.container.add_node(cut, self.x_attr)
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

        # lg
        condy = {'attributes': [('lg', ('a', ('foo', 1)))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 2)  # 3-1=2
        self.assertNotIn('b', bids)  # a should not bid on b.

        # lt
        condy = {'attributes': [('lt', ('a', ('foo', 9)))]}
        cut, _ = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 6)  # 9-3=6

        # eq
        condy = {'attributes': [('eq', ('a', ('foo', 2)))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, _ = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 1)

        # neq
        condy = {'attributes': [('neq', ('a', ('group_1', 'x')))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, _ = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 1)

        # regex
        condy = {'attributes': [('regex', ('a', ('group_1', '^a')))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, _ = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 1)

        # same
        # 1. nothing assigned -> increase bit for both (50%)
        condy = {'compositions': [('same', ('a', 'b'))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 1.5)  # 1 + 0.5 increase
        self.assertIs(res['b'][1], 1.5)  # 1 + 0.5 increase

        # 2. a,b, assigned to sth else -> nothing
        condy = {'compositions': [('same', ('a', 'b'))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut.trigger({'assigned': {'a': ('k', 10), 'b': ('l', 10)},
                                 'bids': []}, 'init')
        # so e.g. only better attribute matches can increase the need for it
        # to bid higher - and eventually stuff getting assigned here.
        self.assertNotIn('a', bids)
        self.assertNotIn('b', bids)

        # diff
        # 1. nothing assigned -> drop one bid
        condy = {'compositions': [('nhare', ('group_1', ['a', 'b']))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 1)  # 1 (type)
        self.assertNotIn('b', bids)  # drop other bid.

        # 2. a assigned, b no bid -> increase bid for b (50%)
        condy = {'compositions': [('share', ('group_1', ['a', 'b']))]}
        cut_x = so.Entity('x', self.map, self.request, self.container, condy)
        cut_y = so.Entity('y', self.map, self.request, self.container, condy)
        self.container.add_node(cut_x, self.x_attr)
        self.container.add_node(cut_y, self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut_x.trigger({'assigned': {'y': ('a', 1)},
                                   'bids': []}, 'init')
        self.assertIs(res['b'][1], 1.5)  # 1 (type) + 0.5 increase

        # 3. a,b, assigned to sth else -> if neighbour bids too -
        # increase bid a bit (25%)
        condy = {'compositions': [('share', ('group_1', ['a', 'b']))]}
        cut_x = so.Entity('x', self.map, self.request, self.container, condy)
        cut_y = so.Entity('y', self.map, self.request, self.container, condy)
        self.container.add_node(cut_x, self.x_attr)
        self.container.add_node(cut_y, self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        res, bids = cut_x.trigger({'assigned': {'a': ('k', 10),
                                                'b': ('l', 10)},
                                   'bids': []}, 'init')
        self.assertIs(bids['b'][1], 1)  # y should bid on b
        self.assertIs(bids['a'][1], 1.25)  # x bid should increase by 0.25

        # share
        # 1. nothing assigned -> increase bit for both (50%)
        condy = {'compositions': [('share', ('group_1', ['a', 'b']))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 1.5)  # 1 + 0.5 increase
        self.assertIs(res['b'][1], 1.5)  # 1 + 0.5 increase

        # 2. a, b assigned somewhere else, ->  nothing
        condy = {'compositions': [('share', ('group_1', ['a', 'b']))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut.trigger({'assigned': {'a': ('k', 10), 'b': ('l', 10)},
                                 'bids': []}, 'init')
        # so e.g. only better attribute matches can increase the need for it
        # to bid higher - and eventually stuff getting assigned here.
        self.assertNotIn('a', bids)
        self.assertNotIn('b', bids)

        # nshare
        # 1. nothing assigned -> drop one bid
        condy = {'compositions': [('nshare', ('group_2', ['a', 'b']))]}
        cut = so.Entity('x', self.map, self.request, self.container, condy)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut.trigger({'assigned': {}, 'bids': []}, 'init')
        self.assertIs(res['a'][1], 1)  # 1 (type)
        self.assertNotIn('b', bids)  # drop other bid.

        # 2. a assigned, b no bid -> increase bid for b (50%)
        condy = {'compositions': [('nshare', ('group_2', ['a', 'b']))]}
        cut_x = so.Entity('x', self.map, self.request, self.container, condy)
        cut_y = so.Entity('y', self.map, self.request, self.container, condy)
        self.container.add_node(cut_x, self.x_attr)
        self.container.add_node(cut_y, self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        self.container.add_node(cut, self.x_attr)
        res, bids = cut_x.trigger({'assigned': {'y': ('a', 1)},
                                   'bids': []}, 'init')
        self.assertIs(res['b'][1], 1.5)  # 1 (type) + 0.5 increase

        # 3. a,b, assigned to sth else -> if neighbour bids too -
        # increase bid a bit (25%)
        condy = {'compositions': [('nshare', ('group_2', ['a', 'b']))]}
        cut_x = so.Entity('x', self.map, self.request, self.container, condy)
        cut_y = so.Entity('y', self.map, self.request, self.container, condy)
        self.container.add_node(cut_x, self.x_attr)
        self.container.add_node(cut_y, self.y_attr)
        self.container.add_edge(cut_x, cut_y)
        res, bids = cut_x.trigger({'assigned': {'a': ('k', 10),
                                                'b': ('l', 10)},
                                   'bids': []}, 'init')
        self.assertIs(bids['b'][1], 1)  # y should bit on b
        self.assertIs(bids['a'][1], 1.25)  # x bid should increse by 0.25


class SelfOptStitcherTest(unittest.TestCase):
    """
    Testcase for the SelfOptStitcher class.
    """

    def setUp(self):
        self.cut = so.SelfOptStitcher()
        self.cut.rels = {'type_x': 'type_a',
                         'type_y': 'type_b',
                         'type_z': 'type_c'}

        self.container = nx.DiGraph()
        self.container.add_node('A', {'type': 'type_a'})
        self.container.add_node('B', {'type': 'type_b'})
        self.container.add_node('C', {'type': 'type_c'})
        self.container.add_edge('A', 'B')
        self.container.add_edge('B', 'C')

        self.request = nx.DiGraph()
        self.request.add_node('X', {'type': 'type_x'})
        self.request.add_node('Y', {'type': 'type_y'})
        self.request.add_node('Z', {'type': 'type_y'})
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

        # TODO: complex test with 2 groups.
