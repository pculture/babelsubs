try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs import storage
from babelsubs.generators.sbv import SBVGenerator

from babelsubs.tests import utils
from babelsubs import load_from


class SBVParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.sbv")
        self.assertEquals(len(subs), 19)
        
    def test_internal_format(self):
        subs  = utils.get_subs("simple.sbv")
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items()]
        self.assertEquals(sub_data[0][0], 48)
        self.assertEquals(sub_data[0][1], 2932)
        self.assertEquals(sub_data[0][2], 'We started Universal Subtitles because we believe')

    def test_line_breaks(self):
        subs  = utils.get_subs("simple.sbv")
        parsed = subs.to_internal()
        nodes = [x for x in parsed.get_subtitles()]
        self.assertEquals(storage.get_contents(nodes[13]), 'We support videos on <br xmlns="http://www.w3.org/ns/ttml"/>YouTube, Blip.TV, Ustream, and many more.')
