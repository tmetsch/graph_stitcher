"""
Unittest for the vis module.
"""

import os
import unittest

import networkx as nx

from stitcher import vis


class TestVisualizations(unittest.TestCase):
    """
    Tests the vis module.
    """

    def setUp(self):
        self.container = nx.DiGraph()
        self.container.add_node('a', {'type': 'a', 'rank': 1})
        self.container.add_node('b', {'type': 'a', 'rank': 5})
        self.container.add_node('c', {'type': 'a', 'rank': 10})
        self.container.add_edge('a', 'b')
        self.container.add_edge('b', 'c')
        self.request = nx.DiGraph()
        self.request.add_node('1', {'type': 'b'})
        self.request.add_node('2', {'type': 'b'})
        self.request.add_edge('1', '2')
        self.container = nx.union(self.container, self.request)
        self.container.add_edge('1', 'a')
        self.container.add_edge('2', 'a')

    def test_show_for_success(self):
        """
        Test the show routine.
        """
        vis.show([self.container], self.request, ['Test'],
                 filename='tmp.png')
        os.remove('tmp.png')

    def test_show3d_for_success(self):
        """
        Test the show routine.
        """
        vis.show_3d([self.container], self.request, ['Test'],
                    filename='tmp.png')
        os.remove('tmp.png')

    def test_show3d_for_failure(self):
        """
        Test the show routine for failure.
        """
        # request nodes are not in container.
        self.container.remove_edge('1', 'a')
        self.container.remove_node('1')
        self.container.remove_edge('2', 'a')
        self.container.remove_node('2')
        self.assertRaises(nx.NetworkXError, vis.show_3d, [self.container],
                          self.request, ['Test'])
