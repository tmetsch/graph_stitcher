"""
Unittest for some basic validators.
"""

import json
import unittest

from networkx.readwrite import json_graph

from stitcher import stitch
from stitcher import validators


class TestIncomingEdgeStitcher(unittest.TestCase):
    """
    Test the simple stitcher class based on # of incoming edges.
    """

    def setUp(self):
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.stitcher = stitch.GlobalStitcher()

    def test_validate_for_success(self):
        """
        Test validate for success.
        """
        res1 = self.stitcher.stitch(self.container, self.request)
        validators.validate_incoming_edges(res1)

    def test_validate_for_failure(self):
        """
        Test validate for failure.
        """
        pass

    def test_validate_for_sanity(self):
        """
        Test validate for sanity.
        """
        res1 = self.stitcher.stitch(self.container, self.request)
        res2 = validators.validate_incoming_edges(res1, {'b': 5})

        self.assertTrue(len(res2) == 8)
        # 4 are ok & 4 are stupid
        count = 0
        for item in res2:
            if res2[item] != 'ok':
                count += 1
        self.assertEqual(count, 4)


class TestNodeRankSticher(unittest.TestCase):
    """
    Test the simple stitcher class based on ranks.
    """

    def setUp(self):
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.stitcher = stitch.GlobalStitcher()

    def test_validate_for_success(self):
        """
        Test validate for success.
        """
        res1 = self.stitcher.stitch(self.container, self.request)
        validators.validate_incoming_rank(res1)

    def test_validate_for_failure(self):
        """
        Test validate for failure.
        """
        pass

    def test_validate_for_sanity(self):
        """
        Test validate for sanity.
        """
        res1 = self.stitcher.stitch(self.container, self.request)
        res2 = validators.validate_incoming_rank(res1, {'a': (0, 3)})

        self.assertTrue(len(res2) == 8)
        self.assertEquals(res2[4],
                          'node B rank is >= 3 and # incoming edges is > 0')
