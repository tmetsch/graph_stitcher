"""
Module implementing the graph stitcher.
"""

import json
import os


class Stitcher(object):
    """
    A stitcher.
    """

    def __init__(self, filename=None):
        """
        Initiate the stitcher.
        """
        if filename is None:
            filename = os.path.dirname(os.path.abspath(__file__)) + os.sep + \
                       '..' + os.sep + 'data' + os.sep + 'stitch.json'
        self.rels = json.load(open(filename, 'r'))

    def stitch(self, container, request, conditions=None):
        """
        Stitch a request graph into an existing graph container. Returns a set
        of possible options.

        :param container: A graph describing the existing container with
            ranks.
        :param request: A graph describing the request.
        :param conditions: Dictionary with conditions - e.g. node a & b need
            to be related to node c.
        :return: List of resulting graphs(s).
        """
        raise NotImplementedError('Not implemented yet.')
