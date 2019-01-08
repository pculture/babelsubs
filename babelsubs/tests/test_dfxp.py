# encoding: utf-8
import copy
import unittest
from unittest import TestCase

from lxml import etree

from babelsubs.parsers.dfxp import (DFXPParser, time_expression_to_milliseconds,
                                   milliseconds_to_time_clock_exp, TIME_EXPRESSION_CLOCK_TIME)
from babelsubs.generators.dfxp import DFXPGenerator
from babelsubs.generators.srt import SRTGenerator
from babelsubs.parsers.base import SubtitleParserError
from babelsubs.storage import SubtitleSet

from babelsubs.tests import utils
from babelsubs import utils as main_utils
from babelsubs import load_from
from babelsubs.xmlconst import *

SRT_TEXT = u"""
1
00:00:01,004 --> 00:00:04,094
Welkom bij de presentatie é over optellen niveau 2

2
00:00:04,094 --> 00:00:07,054
And the message, with non ascii chars caçao.

3
00:00:09,094 --> 00:00:12,054
We need <i>italics</i> <b>bold</b> <u>underline</u> and speaker change >>Hey .


"""

class DFXPParsingTest(TestCase):
    def setUp(self):
        self.subtitle_set = utils.get_subs("simple.dfxp").to_internal()

    def test_basic(self):
        self.assertEquals(len(self.subtitle_set.subtitles), 76)
        subs = utils.get_subs("pre-dmr.dfxp")
        self.assertEquals(len(subs), 419)

    def test_timing_in_milliseconds(self):
        self.assertEquals(self.subtitle_set.subtitles[0].start_time, 1200)
        self.assertEquals(self.subtitle_set.subtitles[0].end_time, 4467)

    def test_formatting(self):
        subtitles = utils.get_subs("with-formatting.dfxp").to_internal().subtitles
        self.assertEqual(subtitles[2].text, 'It has <b>bold</b> formatting')
        self.assertEqual(subtitles[3].text, 'It has <i>italics</i> too')
        self.assertEqual(subtitles[4].text, 'And why not <u>underline</u>')
        # TODO: should we actually allow these kinds of tags to be escaped?
        self.assertEqual(subtitles[5].text,
                         'It has a html tag  should be stripped')
        self.assertEqual(subtitles[6].text,
                         'It has speaker changes >>>')

    def test_xml_literals(self):
        subtitles = utils.get_subs("with-xml-literals.dfxp").to_internal().subtitles
        self.assertEqual(subtitles[2].text,'It has <b>bold</b> formatting')
        self.assertEqual(subtitles[3].text,'It has <i>italics</i> too')
        self.assertEqual(subtitles[4].text,'And why not <u>underline</u>')


    def test_nested_with_markup(self):
        subtitle_set = utils.get_subs("simple.dfxp").to_internal()
        self.assertEqual(subtitle_set.subtitles[38].text, 'a <u>word on <i>nested spans</i></u>')


    def test_self_generate(self):
        subs = utils.get_subs("simple.dfxp")
        parsed = DFXPParser(DFXPGenerator(subs.subtitle_set, 'en').__unicode__())

        for x1, x2 in zip([x for x in subs.to_internal()], [x for x in parsed.to_internal()]):
            self.assertEquals(x1, x2)

    def test_load_from_string(self):
        filename = utils.get_data_file_path('simple.dfxp')
        with open(filename) as f:
            s = f.read()
        load_from(s, type='dfxp').to_internal()

    def test_wrong_format(self):
        with self.assertRaises(SubtitleParserError):
            DFXPParser.parse(SRT_TEXT)

    def test_unsynced_generator(self):
        subs = SubtitleSet('en')
        for x in xrange(0,5):
            subs.append_subtitle(None, None, str(x))
        output = unicode(DFXPGenerator(subs))

        parsed = DFXPParser(output, 'en')
        internal = parsed.to_internal()

        self.assertEqual(len(internal), 5)
        for i, subtitle in enumerate(internal.subtitles):
            self.assertIsNone(subtitle[0])
            self.assertIsNone(subtitle[1])
            self.assertEqual(subtitle[2], str(i))

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            DFXPParser("this\n\nisnot a valid subs format","en")

    def test_whitespace(self):
        subtitle_set = utils.get_subs("pre-dmr.dfxp").subtitle_set
        self.assertEqual(subtitle_set.subtitles[0].text,
                '''Last time, we began talking about<br>resonance structures. And I'd like''')

    def test_equality_ignores_whitespace(self):
        subs_1 = utils.get_subs('pre-dmr.dfxp').subtitle_set
        subs_2 = utils.get_subs('pre-dmr-whitespace.dfxp').subtitle_set
        self.assertEqual(subs_1, subs_2)

    def test_unsynced(self):
        subtitle_set = utils.get_subs('i-2376.dfxp').subtitle_set
        self.assertFalse(subtitle_set.fully_synced)

    def test_regions(self):
        subs = utils.get_subs("regions.dfxp")
        subtitles = subs.to_internal().subtitles
        self.assertEquals(subtitles[0].region, "top")
        for subtitle in subtitles[1:]:
            self.assertEquals(subtitle.region, None)

    def test_f_dfxp(self):
        # tests a pretty feature rich dfpx file
        self.assertRaises(SubtitleParserError, utils.get_subs, "from-n.dfxp")

    def test_unsynced_as_generated_from_frontend(self):
        dfxp = utils.get_subs("dfxp-as-front-end-no-sync.dfxp").to_internal()
        for sub in dfxp.subtitles:
            self.assertEqual(None, sub.start_time)
            self.assertEqual(None, sub.end_time)

class DFXPMultiLines(TestCase):
    def setUp(self):
        self.subtitle_set = utils.get_subs("multiline-italics.dfxp").to_internal()
        self.subtitles = self.subtitle_set.subtitles

    def test_two_line_italics(self):
        """Line break inside italics. """
        expected = "<i>multi-line<br>italicized</i>"
        self.assertEqual(expected, self.subtitles[2].text)

    def test_italics_after_linebreak(self):
        """3 lines with italicized 2nd and 3rd. """
        expected = "this is the first line<br><i>multi-line<br>italicized second and third</i>"
        self.assertEqual(expected, self.subtitles[3].text)

    def test_italics_before_linebreak(self):
        """italicized lines followed by linebreak and regular text."""
        expected = "<i>italicized</i><br>no italics last line"
        self.assertEqual(expected, self.subtitles[4].text)

    def test_linebreak_no_italics(self):
        """Linebreak with no italics"""
        expected = "this is line 1 <br>this is line 2"
        self.assertEqual(expected, self.subtitles[5].text)

    def test_linebreak_before_italics(self):
        """linebreak before italics. """
        expected = "this is line 1 <br><i>italicized</i><br>no italics last line"
        self.assertEqual(expected, self.subtitles[6].text)

    def test_linebreak_in_nested_tags(self):
        """italicized lines followed by linebreak and regular text."""
        expected = "this is line 1 <br><i>italicized <b>this is bold and italics</b></i>" \
                   + "<br>no italics last line"
        self.assertEqual(expected, self.subtitles[7].text)

@unittest.skip
class DFXPMergeTest(TestCase):
    def setUp(self):
        # TODO: fix dfxp merge to actually work
        self.en_subs = SubtitleSet('en')
        self.es_subs = SubtitleSet('es')
        self.fr_subs = SubtitleSet('fr')

        self.en_subs.append_subtitle(1000, 1500, 'content')
        self.es_subs.append_subtitle(1000, 1500, 'spanish content')
        self.es_subs.append_subtitle(2000, 2500, 'spanish content 2',
                                     new_paragraph=True)
        self.fr_subs.append_subtitle(1000, 1500, 'french content')

        self.en_subs = DFXPGenerator.generate(self.en_subs)
        self.es_subs = DFXPGenerator.generate(self.es_subs)
        self.fr_subs = DFXPGenerator.generate(self.fr_subs)

    def test_dfxp_merge(self):
        result = DFXPGenerator.merge_subtitles(
            [self.en_subs, self.es_subs, self.fr_subs])

        utils.assert_long_text_equal(result, """\
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="">
    <head>
        <metadata xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
            <ttm:title/>
            <ttm:description/>
            <ttm:copyright/>
        </metadata>
        <styling xmlns:tts="http://www.w3.org/ns/ttml#styling">
            <style xml:id="amara-style" tts:color="white" tts:fontFamily="proportionalSansSerif" tts:fontSize="18px" tts:textAlign="center"/>
        </styling>
        <layout xmlns:tts="http://www.w3.org/ns/ttml#styling">
            <region xml:id="amara-subtitle-area" style="amara-style" tts:extent="560px 62px" tts:padding="5px 3px" tts:backgroundColor="black" tts:displayAlign="after"/>
        </layout>
    </head>
    <body region="amara-subtitle-area">
        <div xml:lang="en">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">content</p>
            </div>
        </div>
        <div xml:lang="es">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">spanish content</p>
            </div>
            <div>
                <p begin="00:00:02.000" end="00:00:02.500">spanish content 2</p>
            </div>
        </div>
        <div xml:lang="fr">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">french content</p>
            </div>
        </div>
    </body>
</tt>
""")

    def test_merge_with_header(self):
        initial_ttml = etree.fromstring("""\
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
    <head>
        <styling>
            <style xml:id="style" tts:color="foo" tts:fontSize="bar" />
        </styling>

        <layout>
            <region xml:id="region" style="style" tts:extent="foo" tts:origin="bar" />
        </layout>
    </head>
    <body />
</tt>""")

        result = DFXPGenerator.merge_subtitles(
            [self.en_subs, self.es_subs, self.fr_subs],
            initial_ttml=initial_ttml)

        utils.assert_long_text_equal(result, """\
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="">
    <head>
        <styling>
            <style xml:id="style" tts:color="foo" tts:fontSize="bar"/>
        </styling>
        <layout>
            <region xml:id="region" style="style" tts:extent="foo" tts:origin="bar"/>
        </layout>
    </head>
    <body>
        <div xml:lang="en">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">content</p>
            </div>
        </div>
        <div xml:lang="es">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">spanish content</p>
            </div>
            <div>
                <p begin="00:00:02.000" end="00:00:02.500">spanish content 2</p>
            </div>
        </div>
        <div xml:lang="fr">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">french content</p>
            </div>
        </div>
    </body>
</tt>
""")

class TimeHandlingTest(TestCase):
    # TODO: refactor these
    def test_split(self):
        # should looke like 1h:10:20:200
        milliseconds  = (((1 * 3600 ) + (10 * 60 ) + (20 )) * 1000 )  + 200
        components = main_utils.milliseconds_to_time_clock_components(milliseconds)
        self.assertEquals(dict(hours=1,minutes=10, seconds=20, milliseconds=200), components)

    def test_rounding(self):
        milliseconds  = (((1 * 3600 ) + (10 * 60 ) + (20 )) * 1000 )  + 200.40
        components = main_utils.milliseconds_to_time_clock_components(milliseconds)
        self.assertEquals(dict(hours=1, minutes=10, seconds=20, milliseconds=200), components)

    def test_none(self):
        self.assertEquals(dict(hours=0,minutes=0, seconds=0, milliseconds=0), main_utils.milliseconds_to_time_clock_components(0))

    def test_expression(self):
        # should looke like 1h:10:20:200
        milliseconds  = (((1 * 3600 ) + (10 * 60 ) + (20 )) * 1000 )  + 200
        self.assertEquals("01:10:20.200", milliseconds_to_time_clock_exp(milliseconds))

    def test_time_expression_to_milliseconds_clock_time_fraction(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )  + 200
        self.assertEquals(time_expression_to_milliseconds("03:20:40.200"), milliseconds)

    def test_parse_time_expression_clock_time(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )
        self.assertEquals(time_expression_to_milliseconds("03:20:40"), milliseconds)

    def test_parse_time_expression_metric(self):
        self.assertEquals(time_expression_to_milliseconds("10h"), 10 * 3600 * 1000)
        self.assertEquals(time_expression_to_milliseconds("5m"), 5 * 60 * 1000)
        self.assertEquals(time_expression_to_milliseconds("3000s"),  3000 * 1000)
        self.assertEquals(time_expression_to_milliseconds("5000ms"), 5000)

    def test_parse_time_expression_clock_regex(self):
        def _components(expression, hours, minutes, seconds, fraction):
            match = TIME_EXPRESSION_CLOCK_TIME.match(expression)
            self.assertTrue(match)
            self.assertEquals(int(match.groupdict()['hours']), hours)
            self.assertEquals(int(match.groupdict()['minutes']), minutes)
            self.assertEquals(int(match.groupdict()['seconds']), seconds)
            try:
                self.assertEquals(int(match.groupdict()['fraction']), fraction)
            except (ValueError, TypeError):
                self.assertEquals(fraction, None)


        _components("00:03:02", 0, 3, 2, None)
        _components("100:03:02", 100, 3, 2, None)
        _components("100:03:02.200", 100, 3, 2, 200)


    @unittest.skip
    def test_normalize_time(self):
        content_str = open(utils.get_data_file_path("normalize-time.dfxp") ).read()
        dfxp = SubtitleSet('en', content_str)
        subs = dfxp.get_subtitles()
        self.assertTrue(len(dfxp) )
        for el in subs:
            self.assertIn("begin", el.attrib)
            self.assertTrue(TIME_EXPRESSION_CLOCK_TIME.match(el.attrib['begin']))
            self.assertIn("end", el.attrib)
            self.assertTrue(TIME_EXPRESSION_CLOCK_TIME.match(el.attrib['end']))
            self.assertNotIn('dur', el.attrib)
        self.assertEqual(subs[5].attrib['end'], '00:01:05.540')
