
from stitcher import stitch

from networkx.readwrite import json_graph

import json
import unittest
import networkx as nx


class TestFilteringConditions(unittest.TestCase):
    """
    Tests the filter functions and validates that the right candidates are
    eliminated.
    """

    def setUp(self):
        self.container = nx.DiGraph()
        self.container.add_node('1', {'type': 'a'})
        self.container.add_node('2', {'type': 'a', 'foo': 'y'})
        self.container.add_node('3', {'type': 'b', 'foo': 'x'})
        self.container.add_edge('1', '2')
        self.container.add_edge('2', '3')

        self.request = nx.DiGraph()
        self.request.add_node('a', {'type': 'x'})
        self.request.add_node('b', {'type': 'x'})
        self.request.add_edge('a', 'b')

        self.cut = stitch.BaseStitcher()

    def test_filter_for_success(self):
        pass

    def test_filter_for_failure(self):
        pass

    def test_filter_for_sanity(self):
        # none given as condition should results input = output
        input = [1, 2, 3]
        output = stitch.filter(self.container, [1, 2, 3], None)
        self.assertEqual(input, output)

        # node a requires target node to have attribute foo set to y
        condy = {'attributes': {'a': ('foo', 'y')}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 2 options left!
        self.assertEquals(len(res1), 2)

        # node a & b to be placed on same target!
        condy = {'compositions': {'same': ('b', 'a')}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        condy = {'compositions': {'same': ('b', 'a')}}
        res2 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only two options left!
        self.assertTrue(len(res1) == 2)
        self.assertTrue(len(res2) == 2)

        # node a & b to be placed on different target!
        condy = {'compositions': {'diff': ('b', 'a')}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        condy = {'compositions': {'diff': ('b', 'a')}}
        res2 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only two options left!
        self.assertTrue(len(res1) == 2)
        self.assertTrue(len(res2) == 2)


class TestBaseStitcher(unittest.TestCase):
    """
    Test the base stitcher class.
    """

    def setUp(self):
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = stitch.BaseStitcher()

    def test_stitch_for_success(self):
        self.cut.stitch(self.container, self.request)

    def test_stitch_for_failure(self):
        pass

    def test_validate_for_failure(self):
        self.assertRaises(NotImplementedError, self.cut.validate, [])

    def test_stitch_for_sanity(self):
        # basic stitch test
        res1 = self.cut.stitch(self.container, self.request)
        self.assertTrue(len(res1) > 0)
        self.assertTrue(res1[0].number_of_edges()) == \
            self.container.number_of_edges() + 3
        self.assertTrue(res1[0].number_of_nodes()) == \
            self.container.number_of_nodes() + 3

        # let's add a node to the request which does not require to be
        # stitched to the container. Hence added edges = 3!
        self.request.add_node('n', {'type': 'foo', 'rank': 7})
        self.request.add_edge('k', 'n')
        self.request.add_edge('n', 'l')

        self.assertTrue(len(res1) > 0)
        self.assertTrue(res1[0].number_of_edges()) == \
            self.container.number_of_edges() + 3
        self.assertTrue(res1[0].number_of_nodes()) == \
            self.container.number_of_nodes() + 3


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
        self.cut = stitch.IncomingEdgeStitcher()

    def test_validate_for_success(self):
        res1 = self.cut.stitch(self.container, self.request)
        self.cut.validate(res1)

    def test_validate_for_failure(self):
        pass

    def test_validate_for_sanity(self):
        res1 = self.cut.stitch(self.container, self.request)
        res2 = self.cut.validate(res1, {'b': 5})

        self.assertTrue(len(res2) == 8)
        self.assertTrue(res2[0] == 'node C has to many edges: 5')


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
        self.cut = stitch.NodeRankStitcher()

    def test_validate_for_success(self):
        res1 = self.cut.stitch(self.container, self.request)
        self.cut.validate(res1)

    def test_validate_for_failure(self):
        pass

    def test_validate_for_sanity(self):
        res1 = self.cut.stitch(self.container, self.request)
        res2 = self.cut.validate(res1, {'a': (1, 4)})

        self.assertTrue(len(res2) == 8)
        self.assertTrue(res2[4] == 'node B has a high rank.')
