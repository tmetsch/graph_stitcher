"""
Unittest for the evolutionary module.
"""

import itertools
import logging
import unittest
import networkx as nx

from stitcher import evolutionary

FORMAT = "%(asctime)s - %(filename)s - %(lineno)s - " \
         "%(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


class TestCandidate(unittest.TestCase):
    """
    Test abstract class.
    """

    def setUp(self):
        self.cut = evolutionary.Candidate('a')

    def test_eq_for_success(self):
        """
        Test eq for success.
        """
        one = evolutionary.Candidate({'a': '1', 'b': '2'})
        another = evolutionary.Candidate({'a': '1', 'b': '2'})
        self.assertTrue(one == another)

    def test_fitness_for_failure(self):
        """
        Test not impl error.
        """
        self.assertRaises(NotImplementedError, self.cut.fitness)

    def test_mutate_for_failure(self):
        """
        Test not impl error.
        """
        self.assertRaises(NotImplementedError, self.cut.mutate)

    def test_crossover_for_failure(self):
        """
        Test not impl error.
        """
        self.assertRaises(NotImplementedError, self.cut.crossover, None)

    def test_eq_for_sanity(self):
        """
        Objects are the same when there genomics are identical.
        """
        one = evolutionary.Candidate({'a': '1', 'b': '2'})
        another = evolutionary.Candidate({'a': '1', 'b': '2'})
        yet_another = evolutionary.Candidate({'a': '1', 'b': '3'})

        self.assertTrue(one == another)
        self.assertTrue(one != yet_another)
        self.assertIn(another, [one])
        self.assertNotIn(yet_another, [one, another])


class TestGraphCandidate(unittest.TestCase):
    """
    Tests the graph candidate.
    """

    def setUp(self):
        self.container = nx.DiGraph()
        self.container.add_node('1', {'type': 'a', 'group': 'foo', 'foo': 3,
                                      'retest': 'aaa'})
        self.container.add_node('2', {'type': 'a', 'group': 'foo'})
        self.container.add_node('3', {'type': 'a', 'foo': 5, 'retest': 'bbb'})
        self.container.add_node('4', {'type': 'b', 'group': 'foo'})
        self.container.add_node('5', {'type': 'b', 'group': 'bar'})
        self.container.add_node('6', {'type': 'b', 'group': 'bar'})

        self.request = nx.DiGraph()
        self.request.add_node('a', {'type': 'x'})
        self.request.add_node('b', {'type': 'x'})
        self.request.add_node('c', {'type': 'y'})
        self.request.add_node('d', {'type': 'y'})

        self.stitch = {'x': 'a', 'y': 'b'}  # stitch x -> a and y -> b

    def test_fitness_for_success(self):
        """
        Test fitness function for success.
        """
        cut = evolutionary.GraphCandidate({'a': '1', 'c': '4'}, self.stitch,
                                          {}, [], self.request, self.container)
        cut.fitness()
        repr(cut)

    def test_mutate_for_success(self):
        """
        Test mutate function for success.
        """
        cut = evolutionary.GraphCandidate({'a': '1', 'c': '4'}, self.stitch,
                                          {}, ['2'], self.request,
                                          self.container)
        cut.mutate()

    def test_crossover_for_success(self):
        """
        Test crossover function for success.
        """
        cut = evolutionary.GraphCandidate({'a': '1', 'c': '4'}, self.stitch,
                                          {}, [], self.request, self.container)
        partner = evolutionary.GraphCandidate({'a': '2', 'c': '4'},
                                              self.stitch, {}, [],
                                              self.request, self.container)
        cut.crossover(partner)

    # Test for failures - should not happen.

    def test_fitness_for_sanity(self):
        """
        Test fitness function for sanity.
        """
        # a should not be stitched to 3!
        cut = evolutionary.GraphCandidate({'a': '4'}, self.stitch, {}, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 100.0)

        # a needs to be stitched to target node with attr foo = 3
        condy = {'attributes': [('eq', ('a', ('foo', 3)))]}
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 0.0)

        cut = evolutionary.GraphCandidate({'a': '2'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.1)

        condy = {'attributes': [('eq', ('a', ('foo', 9)))]}
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.2)

        # a needs to be stitched to target node with attr foo != 3
        condy = {'attributes': [('neq', ('a', ('foo', 3)))]}
        cut = evolutionary.GraphCandidate({'a': '3'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 0.0)

        cut = evolutionary.GraphCandidate({'a': '2'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 0.0)

        condy = {'attributes': [('neq', ('a', ('foo', 3)))]}
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.1)

        # a needs to be stitched to target node with attr foo > 4
        condy = {'attributes': [('lg', ('a', ('foo', 4)))]}
        cut = evolutionary.GraphCandidate({'a': '3'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 0.0)

        cut = evolutionary.GraphCandidate({'a': '2'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.1)

        condy = {'attributes': [('lg', ('a', ('foo', 4)))]}
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.2)

        # a needs to be stitched to target node with attr foo < 4
        condy = {'attributes': [('lt', ('a', ('foo', 4)))]}
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 0.0)

        cut = evolutionary.GraphCandidate({'a': '2'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.1)

        condy = {'attributes': [('lt', ('a', ('foo', 4)))]}
        cut = evolutionary.GraphCandidate({'a': '3'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.2)

        # node a requires target node to have an attribute retest which starts
        # with an 'c'
        condy = {'attributes': [('regex', ('a', ('retest', '^b')))]}
        cut = evolutionary.GraphCandidate({'a': '2'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.1)
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 10.2)
        cut = evolutionary.GraphCandidate({'a': '3'}, self.stitch, condy, [],
                                          self.request, self.container)
        self.assertEquals(cut.fitness(), 0.0)

        # a and b are stitched to 1
        condy = {'compositions': [('share', ('group', ['a', 'b']))]}
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '1'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 0.0)

        # node c has no group attr.
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '3'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 10.1)

        # c and d stitched to nodes with different group value.
        condy = {'compositions': [('share', ('group', ['c', 'd']))]}
        cut = evolutionary.GraphCandidate({'c': '4', 'd': '5'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 10.2)

        # a and b are stitched to 1
        condy = {'compositions': [('nshare', ('group', ['a', 'b']))]}
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '1'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 10.2)

        # node c has no group attr.
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '3'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 10.1)

        # c and d stitched to nodes with different group value.
        condy = {'compositions': [('nshare', ('group', ['c', 'd']))]}
        cut = evolutionary.GraphCandidate({'c': '4', 'd': '5'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 0.0)

        # a and b stitched to same target.
        condy = {'compositions': [('same', ['a', 'b'])]}
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '1'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 0.0)

        # a and b not stitched to same target.
        condy = {'compositions': [('same', ['b', 'a'])]}
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '2'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 10.0)

        # a and b not stitched to same target.
        condy = {'compositions': [('diff', ['a', 'b'])]}
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '2'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 0.0)

        # a and n stitched to same target.
        condy = {'compositions': [('diff', ['b', 'a'])]}
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '1'}, self.stitch,
                                          condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 10.0)

    def test_special(self):
        """
        Test share condition.
        """
        condy = {'compositions': [('share', ('group', ['a', 'b'])),
                                  ('share', ('group', ['c', 'd']))]}
        cut = evolutionary.GraphCandidate({'a': '1', 'b': '1',
                                           'c': '5', 'd': '6'},
                                          self.stitch, condy, [], self.request,
                                          self.container)
        self.assertEquals(cut.fitness(), 0.0)

    def test_mutate_for_sanity(self):
        """
        Test mutate function for sanity.
        """
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch,
                                          {}, ['2'], self.request,
                                          self.container)
        cut.mutate()
        # gens should have flipped - hard to test otherwise as random is
        # involved.
        self.assertDictEqual({'a': '2'}, cut.gen)

    def test_crossover_for_sanity(self):
        """
        Test crossover function for sanity.
        """
        cut = evolutionary.GraphCandidate({'a': '1'}, self.stitch,
                                          {}, [], self.request, self.container)
        partner = evolutionary.GraphCandidate({'a': '2'},
                                              self.stitch, {}, [],
                                              self.request, self.container)
        child = cut.crossover(partner)
        # child's gens should have been taken from the partner. - hard to test
        # otherwise as random is involved.
        self.assertDictEqual(child.gen, partner.gen)

        # partner has a only non valid mappings
        self.container.add_node('y', {'type': 'boo'})
        partner = evolutionary.GraphCandidate({'a': 'y'},
                                              self.stitch, {}, [],
                                              self.request, self.container)
        child = cut.crossover(partner)
        self.assertTrue(child == cut)


class TestBasicEvolution(unittest.TestCase):
    """
    Tests the filter functions and validates that the right candidates are
    eliminated.
    """

    def setUp(self):
        self.cut = evolutionary.BasicEvolution()

    def test_run_for_success(self):
        """
        Test basic evolutionary algorithm usage.
        """
        population = _get_population('b')
        self.cut.run(population, 1)

    def test_run_for_failure(self):
        """
        Test basic evolutionary algorithm usage for failure.
        """
        population = _get_population('x')
        iterations, _ = self.cut.run(population, 100, stabilizer=True)
        self.assertEquals(iterations, 1)  # should die in second run

        iterations, _ = self.cut.run(population, 0)
        self.assertEquals(iterations, 1)

    def test_run_for_sanity(self):
        """
        Test basic evolutionary algorithm usage.
        """
        population = _get_population('b')
        iteration, _ = self.cut.run(population, 1)
        self.assertEquals(iteration, 0)  # done as we flip to b immediately.


def _get_population(value):
    population = []
    for item in itertools.permutations('abcde'):
        population.append(ExampleCandidate(''.join(item), value))
    return population


class ExampleCandidate(evolutionary.Candidate):
    """
    Simple candidate.
    """

    def __init__(self, gen, test_value):
        super(ExampleCandidate, self).__init__(gen)
        self.test_value = test_value

    def fitness(self):
        """
        Simple but stupid fitness function.
        """
        fit = 0.0
        for item in self.gen:
            if item != self.test_value:
                fit += 1
        return fit

    def mutate(self):
        """
        Not mutating for stable env.
        """
        pass

    def crossover(self, partner):
        """
        To test (get stable environment) let's return a 'bbbbb'
        """
        return self.__class__('bbbbb', self.test_value)

    def __repr__(self):
        return self.gen + ':' + str(self.fitness())
