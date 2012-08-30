try:
    import unittest2 as unittest
except ImportError:
    import unittest

from unittest import TestCase

from babelsubs.generators.srt import SRTGenerator
from babelsubs.parsers.srt import SRTParser

from babelsubs.tests import utils


class SRTParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.srt")
        self.assertEquals(len(subs), 19)
        
    def test_internal_format(self):
        subs  = utils.get_subs("simple.srt")
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items()]
        self.assertEquals(sub_data[0][0], 4)
        self.assertEquals(sub_data[0][1], 2093)
        self.assertEquals(sub_data[0][2], "We started Universal Subtitles because we believe")

    def test_round_trip(self):
        subs1  = utils.get_subs("simple.srt")
        parsed1 = subs1.to_internal()
        srt_ouput = unicode(SRTGenerator(parsed1))
        subs2  = SRTParser(srt_ouput, 'en')
        parsed2 = subs2.to_internal()
        self.assertEquals(len(subs1), len(subs2))
        for x1, x2 in zip([x for x in  parsed1.subtitle_items()], [x for x in parsed2.subtitle_items()]):
            self.assertEquals(x1, x2)
        
    def test_self_generate(self):
        parsed_subs1 = utils.get_subs("simple.srt")
        parsed_subs2 = SRTParser(unicode(parsed_subs1), 'en')

        for x1, x2 in zip([x for x in  parsed_subs1.to_internal()], [x for x in parsed_subs2.to_internal()]):
            self.assertEquals(x1, x2)
