import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest


from unittest import TestCase


from babelsubs.tests import utils


class STRParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.srt")
        self.assertEquals(len(subs), 19)
        
