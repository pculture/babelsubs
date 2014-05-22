# encoding: utf-8
from unittest2 import TestCase
import copy

from lxml import etree

from babelsubs.parsers.dfxp import DFXPParser
from babelsubs.generators.dfxp import DFXPGenerator
from babelsubs.generators.srt import SRTGenerator
from babelsubs.parsers.base import SubtitleParserError
from babelsubs.storage import  (
    SubtitleSet, get_attr, TTML_NAMESPACE_URI, _cleanup_legacy_namespace,
    TTML_NAMESPACE_URI_LEGACY, find_els,
)

from babelsubs.tests import utils
from babelsubs import load_from

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

    def test_basic(self):
        subs = utils.get_subs("simple.dfxp")
        self.assertEquals(len(subs), 76)
        
    def test_internal_format(self):
        subs  = utils.get_subs("simple.dfxp")
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items()]
        self.assertEquals(sub_data[0][0], 1200)
        self.assertEquals(sub_data[0][1], 4467)
        self.assertEquals(sub_data[3][2], 'at least 7,000 years ago.')

    def test_self_generate(self):
        parsed_subs1 = utils.get_subs("simple.dfxp")
        parsed_subs2 = DFXPParser(DFXPGenerator(parsed_subs1.subtitle_set, 'en').__unicode__())

        for x1, x2 in zip([x for x in  parsed_subs1.to_internal()], [x for x in parsed_subs2.to_internal()]):
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
            subs.append_subtitle(None, None,"%s" % x)
        output = unicode(DFXPGenerator(subs))

        parsed = DFXPParser(output, 'en')
        internal = parsed.to_internal()

        subs = [x for x in internal.subtitle_items()]
        self.assertEqual(len(internal), 5)
        for i,sub in enumerate(subs):
            self.assertIsNone(sub[0])
            self.assertIsNone(sub[1])
            self.assertEqual(sub[2], str(i))

        for node in internal.get_subtitles():
            self.assertIsNone(get_attr(node, 'begin'))
            self.assertIsNone(get_attr(node, 'end'))

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            DFXPParser ("this\n\nisnot a valid subs format","en")

    def test_whitespace(self):
        subs = utils.get_subs("pre-dmr.dfxp")
        sub = subs.subtitle_set.subtitle_items(mappings=SRTGenerator.MAPPINGS)[0]
        self.assertEqual(sub.text,
                         '''Last time, we began talking about\nresonance structures. And I'd like''')

    def test_equality_ignores_whitespace(self):
        subs_1 = utils.get_subs('pre-dmr.dfxp').subtitle_set
        subs_2 = utils.get_subs('pre-dmr-whitespace.dfxp').subtitle_set
        self.assertEqual(subs_1, subs_2)

    def test_unsynced(self):
        sset = utils.get_subs('i-2376.dfxp').subtitle_set
        self.assertFalse(sset.fully_synced)

class LegacyDFXPTest(TestCase):

    def test_ttfa(self):
        subs = utils.get_subs("pre-dmr.dfxp")
        self.assertEquals(len(subs), 419)
        # make sure the right namespace is in
        subs.subtitle_set._ttml.tag = '{http://www.w3.org/ns/ttml}tt'
        self.assertEqual(subs.subtitle_set._ttml.nsmap[None] , TTML_NAMESPACE_URI)

        subs = utils.get_subs("pre-dmr2.dfxp")
        self.assertEquals(len(subs), 19)
        # make sure the right namespace is in
        subs.subtitle_set._ttml.tag = '{http://www.w3.org/ns/ttml}tt'

    def test_cleanup_namespace(self):
        input_string = open(utils.get_data_file_path("pre-dmr.dfxp")).read()
        cleaned = _cleanup_legacy_namespace(input_string)
        self.assertEqual(cleaned.find(TTML_NAMESPACE_URI_LEGACY), -1)
        sset = SubtitleSet(language_code='en', initial_data=cleaned)
        self.assertEqual(len(sset), 419)

class DFXPMergeTest(TestCase):
    def test_dfxp_merge(self):
        en_subs = SubtitleSet('en')
        es_subs = SubtitleSet('es')
        fr_subs = SubtitleSet('fr')
        en_subs.append_subtitle(1000, 1500, 'content')
        es_subs.append_subtitle(1000, 1500, 'spanish content')
        es_subs.append_subtitle(2000, 2500, 'spanish content 2',
                                new_paragraph=True)
        fr_subs.append_subtitle(1000, 1500, 'french content')

        correct_xml = """\
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
                <p begin="00:00:01.000" end="00:00:01.500">content</p></div>
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
                <p begin="00:00:01.000" end="00:00:01.500">french content</p></div>
        </div>
    </body>
</tt>
"""
        lang = '{http://www.w3.org/XML/1998/namespace}lang'

        merged = etree.fromstring(DFXPGenerator.merge_subtitles(
            [en_subs, es_subs, fr_subs]))

        self.assertEqual(
            etree.tostring(find_els(merged, '/tt/head')[0]),
            etree.tostring(find_els(en_subs._ttml, '/tt/head')[0]))

        merged_divs = find_els(merged, '/tt/body/div')
        self.assertEqual(len(merged_divs), 3)

        self.assertEqual(merged_divs[0].get(lang), 'en')
        self.assertEqual(merged_divs[1].get(lang), 'es')
        self.assertEqual(merged_divs[2].get(lang), 'fr')

        self.assertNodeContentEqual(merged_divs[0],
                                    find_els(en_subs._ttml, '/tt/body')[0])
        self.assertNodeContentEqual(merged_divs[1],
                                    find_els(es_subs._ttml, '/tt/body')[0])
        self.assertNodeContentEqual(merged_divs[2],
                                    find_els(fr_subs._ttml, '/tt/body')[0])


    def assertNodeContentEqual(self, node, node2):
        self.assertEquals(
            ''.join(etree.tostring(child) for child in node),
            ''.join(etree.tostring(child) for child in node2))
