"""
unittest for the module level stuff.
"""

import unittest

import stitcher


class StitcherTest(unittest.TestCase):
    """
    Testcase for the top level module stuff.
    """

    def setUp(self):
        self.cut = stitcher.Stitcher({'a': 'b'})

    def test_stitch_for_failure(self):
        """
        Test stitch for failure.
        """
        self.assertRaises(NotImplementedError, self.cut.stitch, None, None)
