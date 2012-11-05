from unittest2 import TestCase

from babelsubs.generators.sbv import SBVGenerator
from babelsubs.parsers.sbv import SBVParser

from babelsubs.tests import utils

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
        lines = [text for _, _, text, _ in parsed.subtitle_items(SBVGenerator.MAPPINGS)]
        self.assertEquals(lines[13], 'We support videos on [br]YouTube, Blip.TV, Ustream, and many more.')

    def test_with_information_headers(self):
        # we ignore those headers for now, but at least we shouldn't fail on them
        subs  = utils.get_subs("with-information-header.sbv")
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items()]
        self.assertEquals(sub_data[0][0], 48)
        self.assertEquals(sub_data[0][1], 2932)
        self.assertEquals(sub_data[0][2], 'We started Universal Subtitles because we believe')

    def test_round_trip(self):
        subs1  = utils.get_subs("simple.sbv")
        parsed1 = subs1.to_internal()
        output = unicode(SBVGenerator(parsed1))
        subs2  = SBVParser(output, 'en')
        parsed2 = subs2.to_internal()
        self.assertEquals(len(subs1), len(subs2))
        for x1, x2 in zip([x for x in parsed1.subtitle_items()], [x for x in parsed2.subtitle_items()]):
            self.assertEquals(x1, x2)

