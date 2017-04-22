#!/usr/bin/env python2.7

"""
Sample executor showing the result of the stitching & validation methods.
"""

import argparse
import json
import sys
import logging

from networkx.readwrite import json_graph

from stitcher import evolutionary
from stitcher import bidding
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
    conditions = {}

    if algo == 'evolutionary':
        # to show the true power of this :-)
        conditions = {'compositions': [('diff', ('k', 'l'))]}
        stitcher = evolutionary.EvolutionarySticher()
    elif algo == 'bidding':
        # to show the true power of this :-)
        conditions = {'attributes': [('lt', ('l', ('rank', 9)))]}
        stitcher = bidding.BiddingStitcher()
    else:
        stitcher = stitch.GlobalStitcher()
    graphs = stitcher.stitch(container, request, conditions=conditions)

    if len(graphs) > 0:
        results = validators.validate_incoming_edges(graphs, {'b': 5})
        # XXX: disable this if you do not want to see the results.
        vis.show(graphs, request, results)


if __name__ == '__main__':
    options = ['global', 'evolutionary', 'bidding']
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', choices=options, default='global',
                        help='Select the type of stitching algorithm.')
    algo = parser.parse_args(sys.argv[1:]).a
    main(algo)
