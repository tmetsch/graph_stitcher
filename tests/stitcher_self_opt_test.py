"""
Unittest for the self_opt module.
"""

import logging
import unittest
import networkx as nx

from stitcher import self_opt

FORMAT = "%(asctime)s - %(filename)s - %(lineno)s - " \
         "%(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


class TestEntity(unittest.TestCase):

    def setUp(self):
        self.request = nx.DiGraph()
        self.container = nx.DiGraph()

        self.request.add_node('k', {'type': 'foo'})
        self.request.add_node('l', {'type': 'bar'})
        self.request.add_edge('k', 'l')

        self.container.add_node('x', {'type': 'takes_foo'})
        self.container.add_node('y', {'type': 'takes_bar'})
        self.container.add_edge('x', 'y')

        # how to stitch the types.
        self.map = {'foo': 'takes_foo',
                    'bar': 'takes_bar'}

        # pretty bad random assignment:
        tmp = nx.union(self.container, self.request)
        tmp.add_edge('k', 'y')
        tmp.add_edge('l', 'x')

        self.rnd_assg = nx.DiGraph()
        cache = {}
        for node, attrs in tmp.nodes(data=True):
            entity = self_opt.Entity(node, self.rnd_assg, self.request,
                                     self.map, {})
            self.rnd_assg.add_node(entity, attrs)
            cache[node] = entity
        for src, trg, attrs in tmp.edges(data=True):
            self.rnd_assg.add_edge(cache[src], cache[trg], attrs)

    def test_process_for_success(self):
        """
        Test process routine for success.
        """
        for node in self.rnd_assg:
            if node.node_name in self.container:  # don't need request's nodes.
                node.process()

    def test_step_for_success(self):
        """
        Test step routine for success.
        """
        for node in self.rnd_assg:
            if node.node_name in self.container:
                node.step([], [], -1, None)

    def test_process_for_sanity(self):
        """
        Test process routine for sanity.
        """
        for node in self.rnd_assg:
            if node.node_name in self.container:
                node.process()

        for node in self.rnd_assg:
            if node.node_name in self.container:
                self.assertEqual(node.credits, 100)

        self.assertEqual(len(self.rnd_assg.edges()), 4)
        self.assertIn(('k', 'x'), self.rnd_assg.edges())
        self.assertIn(('l', 'y'), self.rnd_assg.edges())

    def test_eq_for_sanity(self):
        entity_1 = self_opt.Entity('x', None, None, None, None)
        entity_2 = self_opt.Entity('y', None, None, None, None)
        entity_3 = self_opt.Entity('y', None, None, None, None)
        self.assertTrue(entity_1 == 'x')
        self.assertTrue(entity_1 == entity_1)
        self.assertTrue(entity_2 == entity_3)

        self.assertFalse(entity_1 == 'y')
        self.assertFalse(entity_1 == entity_2)
        self.assertFalse(entity_1 == entity_3)

        tmp = nx.DiGraph()
        self.assertFalse(entity_1 == tmp)
