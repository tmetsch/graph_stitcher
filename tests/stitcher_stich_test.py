
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
        self.container.add_node('1', {'type': 'a', 'foo': 'x', 'bar': 5})
        self.container.add_node('2', {'type': 'a', 'foo': 'y', 'bar': 7})
        self.container.add_node('3', {'type': 'b', 'foo': 'x'})
        self.container.add_edge('1', '2')
        self.container.add_edge('2', '3')

        self.request = nx.DiGraph()
        self.request.add_node('a', {'type': 'x'})
        self.request.add_node('b', {'type': 'y'})
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
        condy = {'attributes': {'eq': ('a', ('foo', 'y'))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->2, b->3!
        self.assertEquals(len(res1), 1)

        # node a requires target node to have attribute foo set to 5
        condy = {'attributes': {'eq': ('a', ('bar', 5))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->1, b->3!
        self.assertEquals(len(res1), 1)

        # node a requires target node to have attribute foo not set to y
        condy = {'attributes': {'neq': ('a', ('foo', 'y'))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->1, b->3!
        self.assertEquals(len(res1), 1)

        # node a requires target node to have attribute foo not set to 5
        condy = {'attributes': {'neq': ('a', ('bar', 5))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->2, b->3!
        self.assertEquals(len(res1), 1)

        # node a requires target node to have an attribute foo with value > 5
        condy = {'attributes': {'lg': ('a', ('bar', 6))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->2, b->3!
        self.assertEquals(len(res1), 1)

        # node a requires target node to have an attribute foo with value < 5
        condy = {'attributes': {'lt': ('a', ('bar', 6))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 1 option left - a->1, b->3!
        self.assertEquals(len(res1), 1)

        # # node a requires target node to have an attribute matching a regex
        # condy = {'attributes': {'regex': ('a', ('foo', '\w'))}}
        # res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        # # only 2 options left!
        # self.assertEquals(len(res1), 2)

        self.container.add_node('4', {'type': 'b', 'foo': 'x'})
        self.container.add_edge('3', '4')
        self.request.add_node('c', {'type': 'y'})
        self.request.add_edge('b', 'c')

        # node c & b to be stitched to same target!
        condy = {'compositions': {'same': ('b', 'c')},
                 'attributes': {'eq': ('a', ('foo', 'x'))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        condy = {'compositions': {'same': ('c', 'b')},
                 'attributes': {'eq': ('a', ('foo', 'x'))}}
        res2 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 2 options left: b&c->3 or b&c->4
        self.assertEquals(len(res1), 2)
        self.assertEquals(len(res2), 2)

        # node a & b to be stitched to different targets!
        condy = {'compositions': {'diff': ('b', 'c')},
                 'attributes': {'eq': ('a', ('foo', 'x'))}}
        res1 = self.cut.stitch(self.container, self.request, conditions=condy)
        condy = {'compositions': {'diff': ('c', 'b')},
                 'attributes': {'eq': ('a', ('foo', 'x'))}}
        res2 = self.cut.stitch(self.container, self.request, conditions=condy)
        # only 2 options left: b->3 & c->4 or b->4 & c->3
        self.assertEquals(len(res1), 2)
        self.assertEquals(len(res2), 2)

    def test_complex_filter_for_sanity(self):
        container = nx.DiGraph()
        container.add_node('a', {'type': 'a', 'group': '1', 'geo': 'eu'})
        container.add_node('b', {'type': 'b', 'group': '1'})
        container.add_node('c', {'type': 'a', 'group': '2'})
        container.add_node('d', {'type': 'b', 'group': '2'})
        container.add_edge('a', 'b')
        container.add_edge('b', 'c')
        container.add_edge('c', 'd')

        request = nx.DiGraph()
        request.add_node('1', {'type': 'x'})
        request.add_node('2', {'type': 'y'})
        request.add_node('3', {'type': 'y'})
        request.add_edge('1', '2')
        request.add_edge('1', '3')

        condy = {'compositions': {'share': ('group', ['1', '2']),
                                  'same': ('2', '3')},
                 'attributes': {'eq': ('1', ('geo', 'eu'))}}

        res1 = self.cut.stitch(container, request, conditions=condy)

        # only one option possible
        self.assertEqual(len(res1), 1)
        # verify stitches
        self.assertIn(('1', 'a'), res1[0].edges())
        self.assertIn(('2', 'b'), res1[0].edges())
        self.assertIn(('3', 'b'), res1[0].edges())


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
