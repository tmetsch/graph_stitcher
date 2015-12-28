
from sticher import stich

from networkx.readwrite import json_graph

import json
import unittest


class TestBaseSticher(unittest.TestCase):
    """
    Test the base stichr class.
    """

    def setUp(self):
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = stich.BaseSticher()

    def test_stich_for_success(self):
        self.cut.stich(self.container, self.request)

    def test_stich_for_failure(self):
        pass

    def test_validate_for_failure(self):
        self.assertRaises(NotImplementedError, self.cut.validate, [])

    def test_stich_for_sanity(self):
        res1 = self.cut.stich(self.container, self.request)
        self.assertTrue(len(res1) > 0)
        self.assertTrue(res1[0].number_of_edges()) == \
            self.container.number_of_edges() + 3
        self.assertTrue(res1[0].number_of_nodes()) == \
            self.container.number_of_nodes() + 3


class TestIncomingEdgesticher(unittest.TestCase):
    """
    Test the simple sticher class based on # of incoming edges.
    """

    def setUp(self):
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = stich.IncomingEdgeSticher()

    def test_validate_for_success(self):
        res1 = self.cut.stich(self.container, self.request)
        self.cut.validate(res1)

    def test_validate_for_failure(self):
        pass

    def test_validate_for_sanity(self):
        res1 = self.cut.stich(self.container, self.request)
        res2 = self.cut.validate(res1, {'b': 5})

        self.assertTrue(len(res2) == 8)
        self.assertTrue(res2[0] == 'node C has to many edges: 5')


class TestNodeScoresticher(unittest.TestCase):
    """
    Test the simple sticher class based on scores.
    """

    def setUp(self):
        container_tmp = json.load(open('data/container.json'))
        self.container = json_graph.node_link_graph(container_tmp,
                                                    directed=True)
        request_tmp = json.load(open('data/request.json'))
        self.request = json_graph.node_link_graph(request_tmp,
                                                  directed=True)
        self.cut = stich.NodeScoreSticher()

    def test_validate_for_success(self):
        res1 = self.cut.stich(self.container, self.request)
        self.cut.validate(res1)

    def test_validate_for_failure(self):
        pass

    def test_validate_for_sanity(self):
        res1 = self.cut.stich(self.container, self.request)
        res2 = self.cut.validate(res1, {'a': (1, 4)})

        self.assertTrue(len(res2) == 8)
        self.assertTrue(res2[4] == 'node B has a to high score.')
