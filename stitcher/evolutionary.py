"""
Implements stitching, validation and filtering functions based on
evolutionary algorithm.
"""

import logging
import random
import re

LOG = logging.getLogger()


def _eq_attr(node, attr, gens, container):
    """
    Calcs fitness based on the fact that node need target node to have an attr
    with a certain value.
    """
    trg_nd = container.node[gens[node]]
    if attr[0] not in trg_nd:
        return 10.1
    elif attr[1] != trg_nd[attr[0]]:
        return 10.2
    return 0.0


def _neq_attr(node, attr, gens, container):
    """
    Calcs fitness based on the fact that node's target shall not have an attr
    with a certain value.
    """
    trg_nd = container.node[gens[node]]
    if attr[0] in trg_nd and attr[1] == trg_nd[attr[0]]:
        return 10.1
    return 0.0


def _lg_attr(node, attr, gens, container):
    """
    Calcs fitness based on the fact that node's target node shall have an attr
    with a value larger than the given one.
    """
    trg_nd = container.node[gens[node]]
    if attr[0] not in trg_nd:
        return 10.1
    elif attr[1] >= trg_nd[attr[0]]:
        return 10.2
    return 0.0


def _lt_attr(node, attr, gens, container):
    """
    Calcs fitness based on the fact that node's target node shall have an attr
    with a value smaller than the given one.
    """
    trg_nd = container.node[gens[node]]
    if attr[0] not in trg_nd:
        return 10.1
    elif attr[1] < trg_nd[attr[0]]:
        return 10.2
    return 0.0


def _regex_attr(node, attr, gens, container):
    """
    Calcs fitness based on the fact that node's target node shall have an attr
    with a value smaller than the given one.
    """
    trg_nd = container.node[gens[node]]
    if attr[0] not in trg_nd:
        return 10.1
    elif not re.search(attr[1], trg_nd[attr[0]]):
        return 10.2
    return 0.0


def _same_target(node1, node2, gens):
    """
    Calcs fitness based on the fact that two nodes should share same target.
    """
    shared_tg = None
    for src in gens:
        if shared_tg is None and src in [node1, node2]:
            shared_tg = gens[src]
        elif shared_tg is not None and gens[src] != shared_tg:
            return 10.0
    return 0.0


def _diff_target(node1, node2, gens):
    """
    Calc fitness based on the fact that two nodes should not share same target.
    """
    shared_tg = None
    for src in gens:
        if shared_tg is None and src in [node1, node2]:
            shared_tg = gens[src]
        elif shared_tg is not None and gens[src] == shared_tg:
            return 10.0
    return 0.0


def _share_attr(attrn, node_list, gens, container):
    """
    Calcs fitness based on the fact that two nodes from the request should be
    stitched to two nodes in the container which share the same attribute
    value.
    """
    attrv = None
    for node in node_list:
        trg = gens[node]
        if attrn not in container.node[trg]:
            return 10.1
        elif attrv is None:
            attrv = container.node[trg][attrn]
        elif attrv != container.node[trg][attrn]:
            return 10.2
    return 0.0


def _nshare_attr(attrn, node_list, gens, container):
    """
    Calcs fitness based on the fact that two nodes from the request should be
    stitched to two nodes in the container which do not share the same
    attribute value.
    """
    attrv = None
    for node in node_list:
        trg = gens[node]
        if attrn not in container.node[trg]:
            return 10.1
        elif attrv is None:
            attrv = container.node[trg][attrn]
        elif attrv == container.node[trg][attrn]:
            return 10.2
    return 0.0


def _my_filter(conditions, gens, container):
    """
    Apply filters.
    """
    res = 0.0
    if 'attributes' in conditions:
        for condition in conditions['attributes']:
            para1 = condition[1][0]
            para2 = condition[1][1]
            if condition[0] == 'eq':
                res += _eq_attr(para1, para2, gens, container)
            elif condition[0] == 'neq':
                res += _neq_attr(para1, para2, gens, container)
            elif condition[0] == 'lg':
                res += _lg_attr(para1, para2, gens, container)
            elif condition[0] == 'lt':
                res += _lt_attr(para1, para2, gens, container)
            elif condition[0] == 'regex':
                res += _regex_attr(para1, para2, gens, container)
    if 'compositions' in conditions:
        for condition in conditions['compositions']:
            para1 = condition[1][0]
            para2 = condition[1][1]
            if condition[0] == 'same':
                res += _same_target(para1, para2, gens)
            elif condition[0] == 'diff':
                res += _diff_target(para1, para2, gens)
            elif condition[0] == 'share':
                res += _share_attr(para1, para2, gens, container)
            elif condition[0] == 'nshare':
                res += _nshare_attr(para1, para2, gens, container)
    return res


class Candidate(object):
    """
    A candidate of a population for an evolutionary algorithm
    """

    def __init__(self, gen):
        """
        Initialize the candidate.

        :param gen: The genetics of the candidate
        """
        self.gen = gen

    def fitness(self):
        """
        Calculate the fitness of this candidate based on it's genes.
        :return:
        """
        raise NotImplementedError('Not done yet.')

    def mutate(self):
        """
        Mutate the candidate.
        """
        raise NotImplementedError('Not done yet.')

    def crossover(self, partner):
        """
        Cross this candidate with another one.
        """
        raise NotImplementedError('Not done yet.')

    def __eq__(self, other):
        return self.gen == other.gen


class GraphCandidate(Candidate):
    """
    Candidate within a population. The DNA of this candidate is defined by a
    dictionary of source to target stitches.
    """

    def __init__(self, gen, stitch, conditions, mutation_list, request,
                 container):
        super(GraphCandidate, self).__init__(gen)
        self.stitch = stitch
        self.conditions = conditions
        self.mutation_list = mutation_list
        self.request = request
        self.container = container

    def fitness(self):
        fit = 0.0

        # 1. stitch
        for src in self.gen:
            trg = self.gen[src]
            if self.container.node[trg]['type'] != \
                    self.stitch[self.request.node[src]['type']]:
                fit += 100

        # 2. conditions
        fit += _my_filter(self.conditions, self.gen, self.container)

        return fit

    def mutate(self):
        # let's mutate to an option outside of the shortlisted candidate list.
        src = random.choice(list(self.gen.keys()))

        done = False
        cutoff = len(self.gen)
        i = 0
        while not done and i <= cutoff:
            # break off as there might be no other match available.
            nd_trg = self.mutation_list[random.randint(
                0, len(self.mutation_list) - 1)][0]
            if self.container.node[nd_trg]['type'] == \
                    self.stitch[self.request.node[src]['type']]:
                done = True
                self.gen[src] = nd_trg
            i += 1

    def crossover(self, partner):
        tmp = {}

        for src in self.gen:
            # pick one from partner
            done = False
            nd_trg = ''
            cutoff = len(self.gen)
            i = 0
            while not done and i <= cutoff:
                nd_trg = random.choice(list(partner.gen.values()))
                if self.container.node[nd_trg]['type'] \
                        == self.stitch[self.request.node[src]['type']]:
                    done = True
                i += 1
            if done:
                tmp[src] = nd_trg
            else:
                tmp[src] = self.gen[src]

        return self.__class__(tmp, self.stitch, self.conditions,
                              self.mutation_list, self.request, self.container)

    def __repr__(self):
        return 'f: ' + str(self.fitness()) + ' - ' + repr(self.gen)


class BasicEvolution(object):
    """
    Implements basic evolutionary behaviour.
    """

    def __init__(self, percent_cutoff=0.2, percent_diversity=0.1,
                 percent_mutate=0.1, growth=1.0):
        """
        Initialize.

        :param percent_cutoff: Which top percentage of the population survives.
        :param percent_diversity: Which percentage to randomly add from the
            unfit population portion - keeps diversity up.
        :param percent_mutate: Percentage of the new population which should
            mutate randomly.
        :param growth: growth percentage of the new population to indicate
            growth/shrinking.
        """
        self.cutoff = percent_cutoff
        self.diversity = percent_diversity
        self.mutate = percent_mutate
        self.growth = growth

    def _darwin(self, population):
        """
        Evolve the population - the strongest survive and some randomly picked
        will survive. A certain percentage will mutate.

        :param population: Population list sorted by fitness.
        :return: List of candidates
        """
        # best possible parents
        new_population = population[0:int(len(population) * self.cutoff)]
        div_pool = population[int(len(population) * self.cutoff):-1]

        # diversity - select some random from 'bad' pool
        for _ in range(int(self.diversity * len(div_pool))):
            i = random.randint(0, len(div_pool) - 1)
            new_population.append(div_pool[i])

        # create children
        len_pop = len(population)
        len_new_pop = len(new_population)
        for _ in range(int(len_pop * self.growth) - len_new_pop):
            candidate1 = population[random.randint(0, len_new_pop - 1)]
            candidate2 = population[random.randint(0, len_new_pop - 1)]
            child = candidate1.crossover(candidate2)
            # if child not in new_population:  # TODO: check if helpful.
            new_population.append(child)

        # mutate some
        for _ in range(int(self.mutate * (len_pop - len_new_pop))):
            i = random.randint(len_new_pop, len_pop - 1)
            new_population[i].mutate()

        LOG.debug('New population length: ' + str(len(new_population)))
        return new_population

    def run(self, population, max_runs, fitness_goal=0.0, stabilizer=False):
        """
        Play the game of life.

        :param population: The initial population.
        :param max_runs: Maximum number of iterations.
        :param fitness_goal: Breakoff value for fitness - default 0.0
        :param stabilizer: If True iteration will break off after population
            stabilizes - comes with a slight performance penalty. Note: only
            useful when the population has a stable length (growth=1.0) :-).
        :return: Number of iterations used and the final population.
        """
        # evolve till max iter, 0.0 (goal) or all death
        iteration = 0
        fitness_sum = 0.0
        population.sort(key=lambda candidate: candidate.fitness())
        while iteration <= max_runs:
            LOG.debug('Iteration: ' + str(iteration))

            population = self._darwin(population)
            population.sort(key=lambda candidate: candidate.fitness())

            if population[0].fitness() == fitness_goal:
                LOG.info('Found solution in iteration: ' + str(iteration))
                break

            if stabilizer:
                new_fitness_sum = sum(candidate.fitness() for
                                      candidate in population)
                if new_fitness_sum == fitness_sum:
                    # in the last solution all died...
                    LOG.info('Population stabilized after iteration: ' +
                             str(iteration - 1))
                    break
                fitness_sum = new_fitness_sum

            iteration += 1

        # show results
        if iteration >= max_runs:
            LOG.warn('Maximum number of iterations reached')
        LOG.info('Final population: ' + repr(population))
        return iteration, population
