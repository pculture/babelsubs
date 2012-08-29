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
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items()]
        self.assertEquals(sub_data[0][0], 4)
        self.assertEquals(sub_data[0][1], 2093)
        self.assertEquals(sub_data[0][2], "We started Universal Subtitles because we believe")
