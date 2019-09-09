"""
Module implementing the graph stitcher.
"""

TYPE_ATTR = 'type'


class Stitcher:
    """
    A stitcher.
    """

    def __init__(self, rels):
        """
        Initiate the stitcher.

        ;:param rels: A dictionary defining what type of nodes in the request
            must be stitched to what type of nodes in the container.
        """
        self.rels = rels

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
