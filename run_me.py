#!/usr/bin/env python

"""
Sample executor showing the result of the stitching & validation methods.
"""

import argparse
import json
import sys
import logging

from networkx.readwrite import json_graph

from stitcher import bidding
from stitcher import evolutionary
from stitcher import iterative_repair
from stitcher import stitch
from stitcher import validators
from stitcher import vis

FORMAT = "%(asctime)s - %(filename)s - %(lineno)s - " \
         "%(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


def main(algo):
    """
    main routine.
    """
    container_tmp = json.load(open('data/container.json'))
    container = json_graph.node_link_graph(container_tmp, directed=True)
    request_tmp = json.load(open('data/request.json'))
    request = json_graph.node_link_graph(request_tmp, directed=True)
    rels = json.load(open('data/stitch.json'))
    conditions = {}

    if algo == 'evolutionary':
        # to show the true power of this :-)
        conditions = {'compositions': [('diff', ('k', 'l'))]}
        stitcher = evolutionary.EvolutionarySticher(rels)
    elif algo == 'bidding':
        # to show the true power of this :-)
        conditions = {'attributes': [('lt', ('l', ('rank', 9)))]}
        stitcher = bidding.BiddingStitcher(rels)
    elif algo == 'repair':
        # to show the true power of this :-)
        conditions = {'attributes': [('eq', ('k', ('rank', 5)))]}
        stitcher = iterative_repair.IterativeRepairStitcher(rels)
    else:
        stitcher = stitch.GlobalStitcher(rels)
    graphs = stitcher.stitch(container, request, conditions=conditions)

    if graphs:
        results = validators.validate_incoming_edges(graphs, {'b': 5})
        # XXX: disable this if you do not want to see the results.
        vis.show(graphs, request, results)


if __name__ == '__main__':
    OPT = ['global', 'evolutionary', 'bidding', 'repair']
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-a', choices=OPT, default='global',
                        help='Select the stitching algorithm.')
    ALGO = PARSER.parse_args(sys.argv[1:]).a
    main(ALGO)
