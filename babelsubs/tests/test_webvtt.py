from unittest2 import TestCase

from lxml import etree
from babelsubs.storage import get_contents, SubtitleSet, TTS_NAMESPACE_URI
from babelsubs.generators.webvtt import WEBVTTGenerator
from babelsubs.parsers import SubtitleParserError
from babelsubs.parsers.webvtt	 import WEBVTTParser
from babelsubs.tests import utils

import babelsubs

class WEBVTTParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("basic.vtt")
        self.assertEquals(len(subs), 19)

    def test_round_trip(self):
        subs1  = utils.get_subs("basic.vtt")
        parsed1 = subs1.to_internal()
        srt_ouput = unicode(WEBVTTGenerator(parsed1))
        subs2  = WEBVTTParser(srt_ouput, 'en')
        parsed2 = subs2.to_internal()
        self.assertEquals(len(subs1), len(subs2))

        for x1, x2 in zip([x for x in parsed1.subtitle_items(WEBVTTGenerator.MAPPINGS)], \
                [x for x in parsed2.subtitle_items(WEBVTTGenerator.MAPPINGS)]):
            self.assertEquals(x1, x2)

    def test_timed_data_parses_correctly(self):
        subs = utils.get_data_file_path('timed_text.vtt')
        parsed = babelsubs.load_from_file(subs, type='vtt', language='en')

        self.assertNotEquals(parsed, None)

        try:
            webvtt = parsed.to('vtt')
            self.assertNotEquals(webvtt, None)
        except Exception, e:
            self.fail(e)

    def test_ampersand_escaping(self):
        subs  = utils.get_subs("basic.vtt")
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items(WEBVTTGenerator.MAPPINGS)]
        self.assertEquals(sub_data[16].text,
                          "such as MP4, theora, webM and <i>&amp;</i> HTML 5.")

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            WEBVTTParser ("this\n\nisnot a valid subs format","en")

    def test_mixed_newlines(self):
        # some folks will have valid srts, then edit them on an editor
        # that will save line breaks on the current platform separator
        # e.g. \n on unix , \r...
        # make sure we normalize this stuff
        subs = utils.get_subs("Untimed_text.vtt")
        parsed = subs.to_internal()
        self.assertEqual(len(subs), 43)
        # second sub should have a line break
        self.assertIn('<p begin="99:59:59.000" end="99:59:59.000">I\'m gutted. <br/>Absolutely gutted.</p>',
            parsed.to_xml())

    def test_cue_settings(self):
        subs  = utils.get_subs("cue-settings.vtt")
        self.assertEquals(len(subs), 6)
        self.assertEquals(subs.to_internal().subtitle_items()[0].text,
                          'Hi, my name is Fred')

    def test_voice_span(self):
        subs  = utils.get_subs("voice-span.vtt")
        self.assertEquals(len(subs), 6)
        self.assertEquals(subs.to_internal().subtitle_items()[0].text,
                          'Hi, my name is Fred')

    def test_no_hour_in_time(self):
        subs  = utils.get_subs("no-hour.vtt")
        item = subs.to_internal().subtitle_items()[0]
        self.assertEquals(item.start_time, 1000)
        self.assertEquals(item.end_time, 3000)

class WEBVTTGeneratorTest(TestCase):

    def test_generated_formatting(self):
        dfxp = utils.get_subs("with-formatting.dfxp").to_internal()
        subs = dfxp.subtitle_items(mappings=WEBVTTGenerator.MAPPINGS)
        self.assertEqual(subs[2].text,'It has <b>bold</b> formatting' )
        self.assertEqual(subs[3].text,'It has <i>italics</i> too' )
        self.assertEqual(subs[4].text,'And why not <u>underline</u>' )
        self.assertEqual(subs[5].text,'It has a html tag <a> should be in brackets' )
        self.assertEqual(subs[6].text,'It has speaker changes >>>' )


    def test_generated_formatting(self):
        dfxp = utils.get_subs("with-formatting.dfxp").to_internal()
        subs = dfxp.subtitle_items(mappings=WEBVTTGenerator.MAPPINGS)
        self.assertEqual(subs[2].text,'It has <b>bold</b> formatting' )
        self.assertEqual(subs[3].text,'It has <i>italics</i> too' )
        self.assertEqual(subs[4].text,'And why not <u>underline</u>' )
        self.assertEqual(subs[5].text,
                         'It has a html tag &lt;a&gt; should be escaped' )
        self.assertEqual(subs[6].text,
                         'It has speaker changes &gt;&gt;&gt;' )

    def test_span_around_newline(self):
        source = 'one<span fontStyle="italic"><br/></span>two'
        subs = SubtitleSet('en')
        subs.append_subtitle(0, 1000, source, escape=False)
        items = subs.subtitle_items(mappings=WEBVTTGenerator.MAPPINGS)
        self.assertEqual(items[0].text, 'one<i>\n</i>two')

    def test_space_before_end_span(self):
        source = """<span fontStyle="italic">one<br/>two </span>three<span fontStyle="italic">four.</span>"""
        subs = SubtitleSet('en')
        subs.append_subtitle(0, 1000, source, escape=False)
        items = subs.subtitle_items(mappings=WEBVTTGenerator.MAPPINGS)
        self.assertEqual(items[0].text, '<i>one\ntwo </i>three<i>four.</i>')

class WEBVTTMultiLines(TestCase):
    def setUp(self):
        self.dfxp = utils.get_subs("multiline-italics.dfxp").to_internal()
        
    def test_two_line_italics(self):
        expected = """<i>multi-line\nitalicized</i>"""
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[2], 
                         mappings=WEBVTTGenerator.MAPPINGS))

    def test_more_line_italics(self):
        expected = ("this is the first line\n<i>multi-line\n"
                    "italicized second and third</i>")
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[3], 
                         mappings=WEBVTTGenerator.MAPPINGS))
