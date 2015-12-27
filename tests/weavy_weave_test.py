
from weavy import weave

from networkx.readwrite import json_graph

import json
import unittest


class TestBaseWeaver(unittest.TestCase):
    """
    Test the base weaver class.
    """

    def setUp(self):
        landscape_tmp = json.load(open('data/landscape.json'))
        self.landscape = json_graph.node_link_graph(landscape_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = weave.BaseWeaver()

    def test_weave_for_success(self):
        self.cut.weave(self.landscape, self.request)

    def test_weave_for_failure(self):
        pass

    def test_validate_for_failure(self):
        self.assertRaises(NotImplementedError, self.cut.validate, [])

    def test_weave_for_sanity(self):
        res1 = self.cut.weave(self.landscape, self.request)
        self.assertTrue(len(res1) > 0)
        self.assertTrue(res1[0].number_of_edges()) == \
            self.landscape.number_of_edges() + 3
        self.assertTrue(res1[0].number_of_nodes()) == \
            self.landscape.number_of_nodes() + 3


class TestIncomingEdgeWeaver(unittest.TestCase):
    """
    Test the simple weaver class based on # of incoming edges.
    """

    def setUp(self):
        landscape_tmp = json.load(open('data/landscape.json'))
        self.landscape = json_graph.node_link_graph(landscape_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = weave.IncomingEdgeWeaver()

    def test_validate_for_success(self):
        res1 = self.cut.weave(self.landscape, self.request)
        self.cut.validate(res1)

    def test_validate_for_failure(self):
        pass

    def test_validate_for_sanity(self):
        res1 = self.cut.weave(self.landscape, self.request)
        res2 = self.cut.validate(res1, {'b': 5})

        self.assertTrue(len(res2) == 8)
        self.assertTrue(res2[0] == 'node C has to many edges: 5')


class TestNodeScoreWeaver(unittest.TestCase):
    """
    Test the simple weaver class based on scores.
    """

    def setUp(self):
        landscape_tmp = json.load(open('data/landscape.json'))
        self.landscape = json_graph.node_link_graph(landscape_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = weave.NodeScoreWeaver()

    def test_validate_for_success(self):
        res1 = self.cut.weave(self.landscape, self.request)
        self.cut.validate(res1)

    def test_validate_for_failure(self):
        pass

    def test_validate_for_sanity(self):
        res1 = self.cut.weave(self.landscape, self.request)
        res2 = self.cut.validate(res1, {'a': (1, 4)})

        self.assertTrue(len(res2) == 8)
        self.assertTrue(res2[4] == 'node B has a to high score.')
