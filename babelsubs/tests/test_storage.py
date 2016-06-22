from lxml import etree
from unittest2 import TestCase

from babelsubs import storage
from babelsubs.generators.html import HTMLGenerator
from babelsubs.generators.srt import SRTGenerator
from babelsubs.parsers import SubtitleParserError
from babelsubs.tests import utils
from babelsubs import utils as main_utils

class TimeHandlingTest(TestCase):

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
        self.assertEquals("01:10:20.200", storage.milliseconds_to_time_clock_exp(milliseconds))


    def test_time_expression_to_milliseconds_clock_time_fraction(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )  + 200
        self.assertEquals(storage.time_expression_to_milliseconds("03:20:40.200"), milliseconds)
        
    def test_parse_time_expression_clock_time(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )  
        self.assertEquals(storage.time_expression_to_milliseconds("03:20:40"), milliseconds)


    def test_parse_time_expression_metric(self):
        self.assertEquals(storage.time_expression_to_milliseconds("10h"), 10 * 3600 * 1000)
        self.assertEquals(storage.time_expression_to_milliseconds("5m"), 5 * 60 * 1000)
        self.assertEquals(storage.time_expression_to_milliseconds("3000s"),  3000 * 1000)
        self.assertEquals(storage.time_expression_to_milliseconds("5000ms"), 5000)
        

    def test_parse_time_expression_clock_regex(self):
        def _components(expression, hours, minutes, seconds, fraction):
            match = storage.TIME_EXPRESSION_CLOCK_TIME.match(expression)
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


    def test_normalize_time(self):
        content_str = open(utils.get_data_file_path("normalize-time.dfxp") ).read()
        dfxp = storage.SubtitleSet('en', content_str, normalize_time=True)
        subs = dfxp.get_subtitles()
        self.assertTrue(len(dfxp) )
        for el in subs:
            self.assertIn("begin", el.attrib)
            self.assertTrue(storage.TIME_EXPRESSION_CLOCK_TIME.match(el.attrib['begin']))
            self.assertIn("end", el.attrib)
            self.assertTrue(storage.TIME_EXPRESSION_CLOCK_TIME.match(el.attrib['end']))
            self.assertNotIn('dur', el.attrib)
        self.assertEqual(subs[5].attrib['end'], '00:01:05.540')

class AddSubtitlesTest(TestCase):

    def _paragraphs_in_div(self, el):
        return [x for x in el.getchildren() if x.tag.endswith("}p")]
        
    def test_new_paragraph(self):
        dfxp = storage.SubtitleSet('en')
        # first sub is always a paragraph break ;)
        dfxp.append_subtitle(0, 1000, "paragraph 1 - A")
        dfxp.append_subtitle(1000, 2000, "paragraph 1 - B")
        dfxp.append_subtitle(2000, 3000, "paragraph 2 - A", new_paragraph=True)
        dfxp.append_subtitle(3000, 4000, "paragraph 2 - B", new_paragraph=False)
        dfxp.append_subtitle(3000, 4000, "paragraph 2 - C")
        divs = dfxp._ttml.xpath('/n:tt/n:body/n:div', namespaces={'n': storage.TTML_NAMESPACE_URI})
        self.assertEquals(len(divs), 2)
        self.assertEquals(len(self._paragraphs_in_div(divs[0])), 2)
        self.assertEquals(len(self._paragraphs_in_div(divs[1])), 3)
        sub_lines = dfxp.subtitle_items()

        # make sure subtitle items returns the right metadata
        self.assertTrue(sub_lines[0].meta['new_paragraph'])
        self.assertFalse(sub_lines[1].meta['new_paragraph'])
        self.assertTrue(sub_lines[2].meta['new_paragraph'])
        self.assertFalse(sub_lines[3].meta['new_paragraph'])

    def test_no_timing(self):
        dfxp = storage.SubtitleSet('en')
        dfxp.append_subtitle(0, 1000, "paragraph 1 - A")
        dfxp.append_subtitle(2000, None, "paragraph 1 - B")
        dfxp.append_subtitle(None, None, "paragraph 1 - C")
        items = [x for x in dfxp.subtitle_items()]
        self.assertEquals(len(items), 3)
        self.assertEquals(items[0][0], 0)
        self.assertEquals(items[0][1], 1000)
        self.assertEquals(items[1][0], 2000)
        self.assertEquals(items[1][1], None)
        self.assertEquals(items[2][0], None)
        self.assertEquals(items[2][1], None)
        self.assertFalse(dfxp.fully_synced)
        dfxp = storage.SubtitleSet('en')
        dfxp.append_subtitle(0, 1000, "paragraph 1 - A")
        dfxp.append_subtitle(1000, 2000, "paragraph 1 - B")
        dfxp.append_subtitle(2000, 3000, "paragraph 2 - A", new_paragraph=True)
        dfxp.append_subtitle(3000, 4000, "paragraph 2 - B")
        dfxp.append_subtitle(3000, 4000, "paragraph 2 - C")
        self.assertTrue(dfxp.fully_synced)

        

    def test_escaping(self):
        dfxp = storage.SubtitleSet('en')
        dfxp.append_subtitle(0, 1000, "Hey <a>html anchor</a>", escape=False)
        dfxp.append_subtitle(0, 1000, "Hey <a>html anchor</a>", escape=True)
        self.assertEqual( storage.get_contents(dfxp.get_subtitles()[0]), 'Hey html anchor')
        self.assertEqual( storage.get_contents(dfxp.get_subtitles()[1]), 'Hey <a>html anchor</a>')
        
    def test_escaping_list(self):
        subtitles = ((0, 1000, "Hey <a>html anchor</a>", ),)
        dfxp = storage.SubtitleSet.from_list('en', subtitles)
        self.assertEqual( storage.get_contents(dfxp.get_subtitles()[0]), 'Hey html anchor')

        dfxp = storage.SubtitleSet.from_list('en', subtitles, escape=True)
        self.assertEqual( storage.get_contents(dfxp.get_subtitles()[0]), 'Hey <a>html anchor</a>')

    def test_paragraph_from_list(self):
        subs = []
        for x in xrange(0,10):
            subs.append((x * 1000, x*1000 + 999, "Sub %x" % x , {'new_paragraph': x%2 == 0}))

        dfxp = storage.SubtitleSet.from_list('en', subs)
        self.assertEqual(len(dfxp.get_subtitles()), 10)
        self.assertEqual(len(dfxp.subtitle_items()), 10)
        for i,sub in enumerate(dfxp.subtitle_items()):
            self.assertEqual(sub.meta['new_paragraph'] , i % 2 ==0)

    def test_control_chars_from_list(self):
        subs = [
            # normal sub
            (1000,  1100, "Sub 1", {'new_paragraph': True}),
            # sub with an invalid control char
            (2000,  2100, "Sub 2\x15", {'new_paragraph': False}),
        ]
        dfxp = storage.SubtitleSet.from_list('en', subs)
        subtitle_items = dfxp.subtitle_items()
        self.assertEquals(subtitle_items[0].text, u'Sub 1')
        self.assertEquals(subtitle_items[1].text, u'Sub 2')

    def test_nested_tags(self):
        dfxp = utils.get_subs("simple.dfxp").to_internal()
        self.assertEqual( storage.get_contents(dfxp.get_subtitles()[37]), 'nested spans')
        self.assertEqual( storage.get_contents(dfxp.get_subtitles()[38]), 'a word on nested spans')

    def test_nested_with_markup(self):
        dfxp = utils.get_subs("simple.dfxp").to_internal()
        self.assertEqual( dfxp.get_content_with_markup(dfxp.get_subtitles()[38], SRTGenerator.MAPPINGS),
                          'a <u>word on <i>nested spans</i></u>')

class AccessTest(TestCase):

    def test_indexing(self):
        subs = [
            (0, 1000, 'Hi'),
            (2000, 3000, 'How are you?'),
        ]
        ss = storage.SubtitleSet.from_list('en', subs)
        # make sure that from_list ends up with a usable list
        self.assertIsNotNone(ss[0])
        self.assertIsNotNone(ss[1])

class ParsingTest(TestCase):

    def test_f_dfxp(self):
        # tests a pretty feature rich dfpx file
        self.assertRaises(SubtitleParserError, utils.get_subs, "from-n.dfxp")



    def test_unsynced_as_generated_from_frontend(self):
        dfxp = utils.get_subs("dfxp-as-front-end-no-sync.dfxp").to_internal()
        for sub in dfxp.subtitle_items():
            self.assertEqual(None, sub.start_time)
            self.assertEqual(None, sub.end_time)

    def test_comments(self):
        # test that the subtitle_items() method doesn't throw an exception
        # when there are comments in the DFXP.  See gh-841 for details.
        dfxp = utils.get_subs("comments.dfxp").to_internal()
        list(dfxp.subtitle_items())
        list(dfxp.subtitle_items(mappings=HTMLGenerator.MAPPINGS))

class UpdateTest(TestCase):

    def test_update_start_time(self):
        dfxp = utils.get_subs("pre-dmr.dfxp").to_internal()
        dfxp_updated = utils.get_subs("pre-dmr.dfxp").to_internal()
        for i in xrange(0, len(dfxp)):
            dfxp_updated.update(i, from_ms=1000*i)
        for i,sub in enumerate(dfxp_updated.subtitle_items()):
            self.assertEqual(i * 1000, sub.start_time)


    def test_update_end_time(self):
        dfxp = utils.get_subs("pre-dmr.dfxp").to_internal()
        dfxp_updated = utils.get_subs("pre-dmr.dfxp").to_internal()
        for i in xrange(0, len(dfxp)):
            dfxp_updated.update(i, to_ms=1000*i)
        for i,sub in enumerate(dfxp_updated.subtitle_items()):
            self.assertEqual(i * 1000, sub.end_time)

    def test_update_language_code(self):
        subs = utils.get_subs("simple.dfxp").to_internal()
        subs.set_language('fr')
        lang_attr_name = '{http://www.w3.org/XML/1998/namespace}lang'
        self.assertEquals(subs._ttml.get(lang_attr_name), 'fr')

class SubtitleXMLFormattingTest(TestCase):
    def setUp(self):
        ttml = etree.fromstring('<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en"><head/><body><div/></body></tt>')
        self.subtitles = storage.SubtitleSet.create_with_raw_ttml(ttml)

    def test_empty_subs(self):
        utils.assert_long_text_equal(self.subtitles.to_xml(), """\
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en">
    <head/>
    <body>
        <div/>
    </body>
</tt>
""")


    def test_with_subs(self):
        self.subtitles.append_subtitle(1000, 1500, "content")
        self.subtitles.append_subtitle(2000, 2500, "<i>content</i>", escape=False)
        self.subtitles.append_subtitle(3000, 3500, "  content with space ")
        utils.assert_long_text_equal(self.subtitles.to_xml(), """\
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en">
    <head/>
    <body>
        <div>
            <p begin="00:00:01.000" end="00:00:01.500">content</p>
            <p begin="00:00:02.000" end="00:00:02.500"><i>content</i></p>
            <p begin="00:00:03.000" end="00:00:03.500">  content with space </p>
        </div>
    </body>
</tt>
""")

    def test_with_new_paragraph(self):
        self.subtitles.append_subtitle(1000, 1500, "content")
        self.subtitles.append_subtitle(2000, 2500, "content 2", new_paragraph=True)
        utils.assert_long_text_equal(self.subtitles.to_xml(), """\
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en">
    <head/>
    <body>
        <div>
            <p begin="00:00:01.000" end="00:00:01.500">content</p>
        </div>
        <div>
            <p begin="00:00:02.000" end="00:00:02.500">content 2</p>
        </div>
    </body>
</tt>
""")
