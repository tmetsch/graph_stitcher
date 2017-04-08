"""
contains validation routines.
"""


def validate_incoming_edges(graphs, param=None):
    """
    In case a node of a certain type has more then a threshold of incoming
    edges determine a possible stitches as a bad stitch.
    """
    param = param or {}
    res = {}
    i = 0
    for candidate in graphs:
        res[i] = 'ok'
        for node, values in candidate.nodes(data=True):
            if values['type'] not in param.keys():
                continue
            else:
                tmp = param[values['type']]
            if len(candidate.in_edges(node)) >= tmp:
                res[i] = 'node ' + str(node) + ' has to many edges: ' + \
                         str(len(candidate.in_edges(node)))
        i += 1
    return res


def validate_incoming_rank(graphs, param=None):
    """
    In case a rank of a node and # of incoming edges increases determine
    possible stitches as a bad stitch.
    """
    param = param or {}
    res = {}
    i = 0
    for candidate in graphs:
        res[i] = 'ok'
        for node, values in candidate.nodes(data=True):
            if values['type'] not in param.keys():
                continue
            else:
                tmp = param[values['type']]
            if len(candidate.in_edges(node)) > tmp[0] \
                    and values['rank'] >= tmp[1]:
                res[i] = 'node ' + str(node) + ' rank is >= ' + \
                         str(tmp[1]) + ' and # incoming edges is > ' \
                         + str(tmp[0])
        i += 1
    return res
