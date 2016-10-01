#!/usr/bin/env python2.7

"""
Sample executor showing the result of the stitching & validation methods.
"""

import json
import random
import sys
import logging
import networkx as nx

from networkx.readwrite import json_graph

from stitcher import evolutionary
from stitcher import stitch
from stitcher import vis

FORMAT = "%(asctime)s - %(filename)s - %(lineno)s - " \
         "%(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


def main(use_evol=False):
    """
    main routine.
    """
    container_tmp = json.load(open('data/container.json'))
    container = json_graph.node_link_graph(container_tmp, directed=True)
    request_tmp = json.load(open('data/request.json'))
    request = json_graph.node_link_graph(request_tmp, directed=True)
    stitches = json.load(open('data/stitch.json'))

    # XXX: change this to whatever stitcher you want to use
    stitcher = stitch.IncomingEdgeStitcher()

    if use_evol:
        evo = evolutionary.BasicEvolution(percent_cutoff=0.9,
                                          percent_mutate=0.0)

        condy = {'compositions': {('diff', ('k', 'l'))}}

        # initial population
        population = []
        for _ in range(10):
            tmp = {}
            for item in request.nodes():
                trg_cand = random.choice(list(['A', 'B', 'C', 'D', 'E', 'F']))
                tmp[item] = trg_cand
            population.append(evolutionary.GraphCandidate(tmp, stitches,
                                                          condy, [], request,
                                                          container))

        _, population = evo.run(population,
                                10,  # do 10 steps
                                fitness_goal=-1.0)  # want multiple

        if population[0].fitness() != 0.0:
            print('Please rerun - did not find a viable solution')
            sys.exit(1)

        graphs = []
        for candidate in population:
            if candidate.fitness() == 0.0:
                tmp_graph = nx.union(container, request)
                for item in candidate.gen:
                    tmp_graph.add_edge(item, candidate.gen[item])
                graphs.append(tmp_graph)
    else:
        graphs = stitcher.stitch(container, request)
    results = stitcher.validate(graphs, {'b': 5})

    # XXX: disable this if you do not want to see the results.
    vis.show(graphs, request.nodes(), results)


if __name__ == '__main__':
    USE_EA = False
    if len(sys.argv) == 2 and sys.argv[1] == '-ea':
        USE_EA = True
    main(USE_EA)
