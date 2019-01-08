from unittest import TestCase

from lxml import etree
from babelsubs.storage import SubtitleSet
from babelsubs.generators.srt import SRTGenerator
from babelsubs.parsers import SubtitleParserError
from babelsubs.parsers.srt import SRTParser
from babelsubs.tests import utils

import babelsubs

class SRTParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.srt")
        self.assertEquals(len(subs), 19)
        
    def test_internal_format(self):
        subs  = utils.get_subs("simple.srt")
        parsed = subs.to_internal()
        self.assertEquals(parsed.subtitles[0].start_time, 4)
        self.assertEquals(parsed.subtitles[0].end_time, 2093)
        self.assertEquals(parsed.subtitles[0].text,
                          "We started <b>Universal Subtitles</b> because we believe")

    def test_round_trip(self):
        subs1  = utils.get_subs("simple.srt")
        parsed1 = subs1.to_internal()
        srt_ouput = unicode(SRTGenerator(parsed1))
        subs2  = SRTParser(srt_ouput, 'en')
        parsed2 = subs2.to_internal()
        self.assertEquals(len(subs1), len(subs2))

        # TODO: fix rounding issues with frames/milliseconds conversions
        for x1, x2 in zip(parsed1.subtitles, parsed2.subtitles):
            self.assertEquals(x1, x2)
        
    def test_timed_data_parses_correctly(self):
        subtitle_set = utils.get_subs('timed_text.srt').to_internal()
        self.assertNotEquals(subtitle_set, None)

    def test_curly_brackets(self):
        subs  = utils.get_subs("curly_brackets.srt")
        parsed = subs.to_internal()
        self.assertEquals(len(parsed.subtitles), 1)
        self.assertEquals(parsed.subtitles[0].text, "{ a } {{ b }} c")

    def test_formatting(self):
        subs = u"""1
00:00:00,004 --> 00:00:02,093
We\n started <b>Universal Subtitles</b> <i>because</i> we <u>believe</u>
"""
        parsed1 = SRTParser(subs, 'en').to_internal()
        self.assertEquals(parsed1.subtitles[0].text,
                "We<br> started <b>Universal Subtitles</b> <i>because</i> we <u>believe</u>")

        output = unicode(SRTGenerator(parsed1))
        parsed2 = SRTParser(output, 'en').to_internal()

        for x1, x2 in zip(parsed1.subtitles, parsed2.subtitles):
            self.assertEquals(x1, x2)

    def test_speaker_change(self):
        subs = """1
00:00:00,004 --> 00:00:02,093
And know, Mr. <b>Amara</b> will talk.\n >> Hello, and welcome.
"""
        parsed1 = SRTParser(subs, 'en').to_internal()
        self.assertEquals(len(parsed1), 1)
        subtitle = parsed1.subtitles[0]

        # TODO: check if we should escape into html by default because of formatting
        self.assertEquals(subtitle.text, 'And know, Mr. <b>Amara</b> will talk.<br> &gt;&gt; Hello, and welcome.')

        output = unicode(SRTGenerator(parsed1))
        parsed2 = SRTParser(output, 'en').to_internal()

        for x1, x2 in zip(parsed1.subtitles, parsed2.subtitles):
            self.assertEquals(x1, x2)

    def test_ampersand_escaping(self):
        subtitles = utils.get_subs("simple.srt").to_internal().subtitles
        self.assertEquals(subtitles[16].text,
                          "such as MP4, theora, webM and <i>&amp;</i> HTML 5.")

        subtitle_set = SubtitleSet("en")
        subtitle_set.append_subtitle(0, 1000, "such as MP4, theora, webM &amp; HTML 5.")
        generated = unicode(SRTGenerator(subtitle_set)).split('\r\n')
        self.assertEquals(generated[2], "such as MP4, theora, webM & HTML 5.")

    def test_unsynced_generator(self):
        subtitle_set = SubtitleSet('en')
        for x in xrange(0,5):
            subtitle_set.append_subtitle(None, None, str(x))
        output = unicode(SRTGenerator(subtitle_set))

        subtitle_set = SRTParser(output,'en').to_internal()
        self.assertEqual(len(subtitle_set), 5)

        for subtitle in subtitle_set.subtitles:
            self.assertEqual(subtitle.start_time, None)
            self.assertEqual(subtitle.end_time, None)

        generated = SRTGenerator(subtitle_set)
        self.assertEqual(generated.format_time(None), u'99:59:59,999')
        self.assertIn(u'''1\r\n99:59:59,999 --> 99:59:59,999\r\n0\r\n\r\n2\r\n99:59:59,999 --> 99:59:59,999\r\n1\r\n\r\n3\r\n99:59:59,999 --> 99:59:59,999\r\n2\r\n\r\n4\r\n99:59:59,999 --> 99:59:59,999\r\n3\r\n\r\n5\r\n99:59:59,999 --> 99:59:59,999\r\n4\r\n''',
                    unicode(generated))


    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            SRTParser("this\n\nisnot a valid subs format","en")

    def test_mixed_newlines(self):
        # some folks will have valid srts, then edit them on an editor
        # that will save line breaks on the current platform separator
        # e.g. \n on unix , \r...
        # make sure we normalize this stuff
        subtitle_set = utils.get_subs("Untimed_text.srt").to_internal()
        self.assertEqual(len(subtitle_set), 43)
        # second sub should have a line break
        self.assertEqual(subtitle_set.subtitles[1].text, "I'm gutted. <br>Absolutely gutted.")

    def test_complex_formatting(self):
        # this is the srt used in our selenium tests
        subtitle_set = utils.get_subs("Timed_en.srt")
        self.assertEqual(len(subtitle_set), 72)
