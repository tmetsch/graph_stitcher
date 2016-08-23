
import itertools
import logging
import unittest

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
        iter, pop = self.cut.run(population, 100)
        self.assertEquals(iter, 1)  # should die in second run, 1st = mutate

        iter, pop = self.cut.run(population, 0)
        self.assertEquals(iter, 1)  # should die in second run, 1st = mutate


    def test_run_for_sanity(self):
        """
        Test basic evolutionary algorithm usage.
        """
        population = _get_population('b')
        iteration, _ = self.cut.run(population, 1)
        self.assertEquals(iteration, 0)


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
