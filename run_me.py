#!/usr/bin/env python2.7

import json

from networkx.readwrite import json_graph

from sticher import stich
from sticher import vis


def main():
    container_tmp = json.load(open('data/container.json'))
    container = json_graph.node_link_graph(container_tmp, directed=True)
    request_tmp = json.load(open('data/request.json'))
    request = json_graph.node_link_graph(request_tmp, directed=True)


    # TODO: allow for chaining of validators & stichers
    # XXX: change this to whatever sticher you want to use
    sticher = stich.IncomingEdgeSticher()
    # sticher = stich.NodeRankSticher()
    containers = sticher.stich(container, request)
    results = sticher.validate(containers, {'b': 5})
    # results = sticher.validate(containers, {'a': (1, 4)})

    # XXX: disable this if you do not want to see the results.
    vis.show(containers, request.nodes(), results)


if __name__ == '__main__':
    main()
