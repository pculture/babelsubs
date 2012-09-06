# encoding: utf-8
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs.tests import utils

class SSAParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.ssa")
        self.assertEquals(len(subs), 19)
