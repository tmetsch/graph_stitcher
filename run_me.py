#!/usr/bin/env python2.7

"""
Sample executor showing the result of the stitching & validation methods.
"""

import json

from networkx.readwrite import json_graph

from stitcher import stitch
from stitcher import vis


def main():
    """
    main routine.
    """
    container_tmp = json.load(open('data/container.json'))
    container = json_graph.node_link_graph(container_tmp, directed=True)
    request_tmp = json.load(open('data/request.json'))
    request = json_graph.node_link_graph(request_tmp, directed=True)

    # XXX: change this to whatever stitcher you want to use
    stitcher = stitch.IncomingEdgeStitcher()
    # stitcher = stitch.NodeRankStitcher()
    graphs = stitcher.stitch(container, request)
    results = stitcher.validate(graphs, {'b': 5})
    # results = stitcher.validate(graphs, {'a': (1, 4)})

    # XXX: disable this if you do not want to see the results.
    vis.show(graphs, request.nodes(), results)


if __name__ == '__main__':
    main()
