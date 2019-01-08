# encoding: utf-8
import unittest
from unittest import TestCase

from babelsubs import SubtitleParserError
from babelsubs.tests import utils
from babelsubs.generators.ssa import SSAGenerator
from babelsubs.parsers.ssa import SSAParser
from babelsubs import storage
from babelsubs.xmlconst import *

class SSAParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.ssa")
        self.assertEquals(len(subs), 19)

    def test_formatting(self):
        subs = """[Script Info]
        Title:
        [Events]
        Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        Dialogue: 0,0:00:00.04,0:00:02.93,Default,,0000,0000,0000,,We\\n started {\\b1}Universal Subtitles{\\b0} {\i1}because{\i0} we {\u1}believe{\u0}"""
        subtitle_set = SSAParser(subs, 'en').subtitle_set
        self.assertEquals(len(subtitle_set), 1)

        # make sure timing looks right
        self.assertEqual(subtitle_set.subtitles[0].start_time, 40)
        self.assertEqual(subtitle_set.subtitles[0].end_time, 2930)

        expected = "We<br> started <b>Universal Subtitles</b> <i>because</i> we <u>believe</u>"
        self.assertEquals(subtitle_set.subtitles[0].text, expected)

        output = unicode(SSAGenerator(subtitle_set))
        subtitle_set2 = SSAParser(output, 'en').subtitle_set

        self.assertEquals(subtitle_set.subtitles, subtitle_set2.subtitles)

    def test_timing_parser(self):
        subtitle_set = utils.get_subs("simple.ssa").to_internal()
        self.assertEqual(subtitle_set.subtitles[0].start_time, 40)
        self.assertEqual(subtitle_set.subtitles[0].end_time, 2930)

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            SSAParser ("this\n\nisnot a valid subs format","en")


class SSAGenerationTest(TestCase):
    def test_newlines(self):
        subtitle_set = storage.SubtitleSet('en')
        subtitle_set.append_subtitle(0, 1000, "line1<br/>line2")
        generated = unicode(SSAGenerator(subtitle_set))
        self.assertIn("line1\Nline2", generated)

    def test_self_generate(self):
        subtitle_set = utils.get_subs("simple.ssa").to_internal()
        generated = SSAParser(unicode(SSAGenerator(subtitle_set)), 'en').to_internal()

        for x1, x2 in zip(subtitle_set.subtitles, generated.subtitles):
            self.assertEquals(x1, x2)

    def test_generate_centiseconds(self):
        subtitle_set = storage.SubtitleSet('en')
        subtitle_set.append_subtitle(133, 238, 'hey')
        output = unicode(SSAGenerator(subtitle_set))
        # make sure time is 230 milliseconds not 38 and that
        # we are rounding to 0.24 (instead of truncating to 0.23
        self.assertIn("Dialogue: 0,0:00:00.13,0:00:00.24", output)

    def test_timing_generator(self):
        subtitle_set = storage.SubtitleSet('en')
        subtitle_set.append_subtitle(40, 2930,"We started Universal Subtitles because we believe")
        generated = unicode(SSAGenerator(subtitle_set))
        self.assertIn('Dialogue: 0,0:00:00.04,0:00:02.93,Default,,0000,0000,0000,,We started Universal Subtitles because we believe', generated)

    def test_unsynced_generator(self):
        subtitle_set = storage.SubtitleSet('en')
        for x in xrange(0,5):
            subtitle_set.append_subtitle(None, None,"%s" % x)
        output = unicode(SSAGenerator(subtitle_set))

        subtitle_set = SSAParser(output,'en').subtitle_set
        self.assertEqual(len(subtitle_set), 5)
        for subtitle in subtitle_set.subtitles:
            self.assertEqual(subtitle.start_time, None)
            self.assertEqual(subtitle.end_time, None)
        generated = SSAGenerator(subtitle_set)
        self.assertEqual(generated.format_time(None), u'9:59:59.99')
        self.assertIn(u'Dialogue: 0,9:59:59.99,9:59:59.99,Default,,0000,0000,0000,,2', unicode(generated))

