#!/usr/bin/env python2.7

import json

from networkx.readwrite import json_graph

from weavy import weave
from weavy import vis


def main():
    landscape_tmp = json.load(open('data/landscape.json'))
    landscape = json_graph.node_link_graph(landscape_tmp, directed=True)
    request_tmp = json.load(open('data/request.json'))
    request = json_graph.node_link_graph(request_tmp, directed=True)

    # XXX: change this to whatever weaver you want to use
    in_weaver = weave.IncomingEdgeWeaver()
    # score_weaver = weave.NodeScoreWeaver()
    landscapes = in_weaver.weave(landscape, request)
    results = in_weaver.validate(landscapes, {'b': 5})
    # results = score_weaver.validate(landscapes, {'a': (1, 4)})

    # XXX: disable this if you do not want to see the results.
    vis.show(landscapes, request.nodes(), results)


if __name__ == '__main__':
    main()
