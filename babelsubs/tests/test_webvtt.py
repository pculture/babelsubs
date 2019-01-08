from unittest import TestCase

from lxml import etree
from babelsubs.storage import SubtitleSet
from babelsubs.generators.webvtt import WEBVTTGenerator
from babelsubs.parsers import SubtitleParserError
from babelsubs.parsers.webvtt import WEBVTTParser
from babelsubs.tests import utils

# TODO: don't forget to change this when you move the timing expressions
from babelsubs.parsers.dfxp import time_expression_to_milliseconds

import babelsubs
import unittest

class WEBVTTParsingTest(TestCase):

    def test_basic(self):
        subtitle_set = utils.get_subs("basic.vtt")
        self.assertEquals(len(subtitle_set), 19)

    def test_round_trip(self):
        # TODO: fix frame rounding discrepancy
        parsed1 = utils.get_subs("basic.vtt").to_internal()
        srt_ouput = unicode(WEBVTTGenerator(parsed1))
        parsed2 = WEBVTTParser(srt_ouput, 'en').to_internal()
        for x1, x2 in zip(parsed1.subtitles, parsed2.subtitles):
            self.assertEquals(x1, x2)

    def test_timed_data_parses_correctly(self):
        subtitle_set = utils.get_subs('timed_text.vtt').to_internal()
        start_time = time_expression_to_milliseconds("00:00:00.028")
        end_time = time_expression_to_milliseconds("00:00:01.061")
        self.assertEquals(subtitle_set.subtitles[0].start_time, start_time)
        self.assertEquals(subtitle_set.subtitles[0].end_time, end_time)

    def test_ampersand_escaping(self):
        subtitle_set = utils.get_subs("basic.vtt").to_internal()
        self.assertEquals(subtitle_set.subtitles[16].text,
                          "such as MP4, theora, webM and <i>&amp;</i> HTML 5.")

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            WEBVTTParser("this\n\nisnot a valid subs format","en")

    def test_mixed_newlines(self):
        # some folks will have valid srts, then edit them on an editor
        # that will save line breaks on the current platform separator
        # e.g. \n on unix , \r...
        # make sure we normalize this stuff
        subtitle_set = utils.get_subs("Untimed_text.vtt").to_internal()
        self.assertEqual(len(subtitle_set), 43)
        # second sub should have a line break
        self.assertEquals(subtitle_set.subtitles[1].text, 'I\'m gutted. <br>Absolutely gutted.')

    def test_cue_settings(self):
        subtitle_set = utils.get_subs("cue-settings.vtt").to_internal()
        self.assertEquals(len(subtitle_set), 6)
        self.assertEquals(subtitle_set.subtitles[0].text,
                          'Hi, my name is Fred')

    def test_voice_span(self):
        subtitle_set = utils.get_subs("voice-span.vtt").to_internal()
        self.assertEquals(len(subtitle_set), 6)
        self.assertEquals(subtitle_set.subtitles[0].text, 'Hi, my name is Fred')

    def test_no_hour_in_time(self):
        subtitle_set = utils.get_subs("no-hour.vtt").to_internal()
        self.assertEquals(subtitle_set.subtitles[0].start_time, 1000)
        self.assertEquals(subtitle_set.subtitles[0].end_time, 3000)

    def test_regions(self):
        subtitles = utils.get_subs("regions.vtt").to_internal().subtitles
        for subtitle in subtitles[:4]:
            self.assertEquals(subtitle.region, "top")
        for subtitle in subtitles[4:]:
            self.assertEquals(subtitle.region, None)

class WEBVTTGeneratorTest(TestCase):
    def setUp(self):
        self.subtitle_set = utils.get_subs("with-formatting.dfxp").to_internal()
        self.generated = unicode(WEBVTTGenerator(self.subtitle_set))

    def test_generated_formatting(self):
        print(self.generated)
        self.assertIn('It has <b>bold</b> formatting', self.generated)
        self.assertIn('It has <i>italics</i> too', self.generated)
        self.assertIn('And why not <u>underline</u>', self.generated)
        self.assertIn('It has a html tag  should be stripped', self.generated)
        self.assertIn('It has speaker changes >>>', self.generated)
        self.assertNotIn('<br>', self.generated)

    def test_regions(self):
        subs = SubtitleSet('en')
        sub = subs.append_subtitle(0, 1000, "test", region="top")
        generator = WEBVTTGenerator(subs)
        self.assertEqual(generator.format_cue_header(subs.subtitles[0]),
                         u'00:00:00.000 --> 00:00:01.000 line:1')
