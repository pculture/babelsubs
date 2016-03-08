from unittest2 import TestCase

from lxml import etree
from babelsubs.storage import get_contents, SubtitleSet, TTS_NAMESPACE_URI
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
        sub_data = [x for x in parsed.subtitle_items(SRTGenerator.MAPPINGS)]
        self.assertEquals(sub_data[0].start_time, 4)
        self.assertEquals(sub_data[0].end_time, 2093)
        self.assertEquals(sub_data[0].text, "We started <b>Universal Subtitles</b> because we believe")

    def test_round_trip(self):
        subs1  = utils.get_subs("simple.srt")
        parsed1 = subs1.to_internal()
        srt_ouput = unicode(SRTGenerator(parsed1))
        subs2  = SRTParser(srt_ouput, 'en')
        parsed2 = subs2.to_internal()
        self.assertEquals(len(subs1), len(subs2))

        for x1, x2 in zip([x for x in parsed1.subtitle_items(SRTGenerator.MAPPINGS)], \
                [x for x in parsed2.subtitle_items(SRTGenerator.MAPPINGS)]):
            self.assertEquals(x1, x2)
        
    def test_timed_data_parses_correctly(self):
        subs = utils.get_data_file_path('timed_text.srt')
        parsed = babelsubs.load_from_file(subs, type='srt', language='en')

        self.assertNotEquals(parsed, None)

        try:
            srt = parsed.to('srt')
            self.assertNotEquals(srt, None)
        except Exception, e:
            self.fail(e)

    def test_curly_brackets(self):
        subs  = utils.get_subs("curly_brackets.srt")
        parsed = subs.to_internal()
        sub_data = list(parsed.subtitle_items(SRTGenerator.MAPPINGS))
        self.assertEquals(len(sub_data), 1)
        self.assertEquals(sub_data[0].text, "{ a } {{ b }} c")

    def test_formatting(self):
        subs = u"""1
00:00:00,004 --> 00:00:02,093
We\n started <b>Universal Subtitles</b> <i>because</i> we <u>believe</u>
"""
        parsed = SRTParser(subs, 'en')
        internal = parsed.to_internal()

        self.assertEquals(len(parsed), 1)
        element = internal.get_subtitles()[0]

        self.assertEquals(len(element.getchildren()), 4)
        br, bold, italics, underline = element.getchildren()

        self.assertEquals(br.text, None)
        self.assertEquals(' started ', br.tail)
        self.assertEquals(br.tag, '{http://www.w3.org/ns/ttml}br')

        self.assertEquals(bold.text, 'Universal Subtitles')
        self.assertEquals(bold.tail, ' ')
        self.assertEquals(bold.tag, '{http://www.w3.org/ns/ttml}span')
        self.assertIn('{%s}fontWeight' % TTS_NAMESPACE_URI, bold.attrib)
        self.assertEquals(bold.attrib['{%s}fontWeight' % TTS_NAMESPACE_URI], 'bold')

        self.assertEquals(italics.text, 'because')
        self.assertEquals(italics.tail, ' we ')
        self.assertEquals(italics.tag, '{http://www.w3.org/ns/ttml}span')
        self.assertIn('{%s}fontStyle' % TTS_NAMESPACE_URI, italics.attrib)
        self.assertEquals(italics.attrib['{%s}fontStyle' % TTS_NAMESPACE_URI], 'italic')

        self.assertEquals(underline.text, 'believe')
        self.assertEquals(underline.tail, None)
        self.assertEquals(underline.tag, '{http://www.w3.org/ns/ttml}span')
        self.assertIn('{%s}textDecoration' % TTS_NAMESPACE_URI, underline.attrib)
        self.assertEquals(underline.attrib['{%s}textDecoration' % TTS_NAMESPACE_URI], 'underline')

        output = unicode(SRTGenerator(internal))
        parsed2 = SRTParser(output, 'en')
        internal2 = parsed2.to_internal()

        for x1, x2 in zip([x for x in internal.subtitle_items(SRTGenerator.MAPPINGS)], \
                [x for x in internal2.subtitle_items(SRTGenerator.MAPPINGS)]):
            self.assertEquals(x1, x2)

    def test_speaker_change(self):
        subs = """1
00:00:00,004 --> 00:00:02,093
And know, Mr. <b>Amara</b> will talk.\n >> Hello, and welcome.
"""
        parsed = SRTParser(subs, 'en')
        internal = parsed.to_internal()

        self.assertEquals(len(parsed), 1)
        element = internal.get_subtitles()[0]
        self.assertTrue(len(element.getchildren()), 2)

        self.assertEquals(get_contents(element), 'And know, Mr. Amara will talk. >> Hello, and welcome.')
        self.assertEquals(etree.tostring(element).strip(),
                          '<p xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" begin="00:00:00.004" end="00:00:02.093">And know, Mr. <span tts:fontWeight="bold">Amara</span> will talk.<br/> &gt;&gt; Hello, and welcome.</p>')
        self.assertEquals(element.getchildren()[1].tail, ' >> Hello, and welcome.')

        output = unicode(SRTGenerator(internal))
        parsed2 = SRTParser(output, 'en')
        internal2 = parsed2.to_internal()

        for x1, x2 in zip([x for x in internal.subtitle_items(SRTGenerator.MAPPINGS)], \
                [x for x in internal2.subtitle_items(SRTGenerator.MAPPINGS)]):
            self.assertEquals(x1, x2)

    def test_ampersand_escaping(self):
        subs  = utils.get_subs("simple.srt")
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items(SRTGenerator.MAPPINGS)]
        self.assertEquals(sub_data[16].text,
                          "such as MP4, theora, webM and <i>&amp;</i> HTML 5.")

    def test_unsynced_generator(self):
        subs = SubtitleSet('en')
        for x in xrange(0,5):
            subs.append_subtitle(None, None,"%s" % x)
        output = unicode(SRTGenerator(subs))

        parsed = SRTParser(output,'en')
        internal = parsed.to_internal()

        subs = [x for x in internal.subtitle_items()]
        self.assertEqual(len(internal), 5)

        for i,sub in enumerate(subs):
            self.assertEqual(sub.start_time, None)
            self.assertEqual(sub.end_time, None)

        generated = SRTGenerator(internal)
        self.assertEqual(generated.format_time(None), u'99:59:59,999')
        self.assertIn(u'''1\r\n99:59:59,999 --> 99:59:59,999\r\n0\r\n\r\n2\r\n99:59:59,999 --> 99:59:59,999\r\n1\r\n\r\n3\r\n99:59:59,999 --> 99:59:59,999\r\n2\r\n\r\n4\r\n99:59:59,999 --> 99:59:59,999\r\n3\r\n\r\n5\r\n99:59:59,999 --> 99:59:59,999\r\n4\r\n''',
                    unicode(generated))


    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            SRTParser ("this\n\nisnot a valid subs format","en")

    def test_mixed_newlines(self):
        # some folks will have valid srts, then edit them on an editor
        # that will save line breaks on the current platform separator
        # e.g. \n on unix , \r...
        # make sure we normalize this stuff
        subs = utils.get_subs("Untimed_text.srt")
        parsed = subs.to_internal()
        self.assertEqual(len(subs), 43)
        # second sub should have a line break
        self.assertIn('<p begin="99:59:59.000" end="99:59:59.000">I\'m gutted. <br/>Absolutely gutted.</p>',
            parsed.to_xml())

    def test_complex_formatting(self):
        # this is the srt used in our selenium tests
        subs = utils.get_subs("Timed_en.srt")
        self.assertEqual(len(subs), 72)

class SRTGeneratorTest(TestCase):

    def setUp(self):
        self.dfxp = utils.get_subs("with-formatting.dfxp").to_internal()
        self.subs = self.dfxp.subtitle_items(mappings=SRTGenerator.MAPPINGS)

    def test_generated_formatting(self):
        self.assertEqual(self.subs[2].text,'It has <b>bold</b> formatting' )
        self.assertEqual(self.subs[3].text,'It has <i>italics</i> too' )
        self.assertEqual(self.subs[4].text,'And why not <u>underline</u>' )
        self.assertEqual(self.subs[5].text,
                         'It has a html tag &lt;a&gt; should be escaped' )
        self.assertEqual(self.subs[6].text,
                         'It has speaker changes &gt;&gt;&gt;')

class SRTMultiLines(TestCase):
    def setUp(self):
        self.dfxp = utils.get_subs("multiline-italics.dfxp").to_internal()
        
    def test_two_line_italics(self):
        """Line break inside italics. """
        expected = """<i>multi-line\r\nitalicized</i>"""
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[2], 
                         mappings=SRTGenerator.MAPPINGS))

    def test_italics_after_linebreak(self):
        """3 lines with italicized 2nd and 3rd. """
        expected = ("this is the first line\r\n<i>multi-line\r\n"
                    "italicized second and third</i>")
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[3], 
                         mappings=SRTGenerator.MAPPINGS))

    def test_italics_before_linebreak(self):
        """italicized lines followed by linebreak and regular text."""
        expected = ("<i>italicized</i>\r\nno italics last line")
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[4], 
                         mappings=SRTGenerator.MAPPINGS))

    def test_linebreak_no_italics(self):
        """Linebreak with no italics"""
        expected = ('this is line 1 \r\nthis is line 2')
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[5], 
                         mappings=SRTGenerator.MAPPINGS))

    def test_linebreak_before_italics(self):
        """linebreak before italics. """
        expected = ('this is line 1 \r\n<i>italicized</i>\r\nno italics last line')
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[6], 
                         mappings=SRTGenerator.MAPPINGS))

    def test_linebreak_in_nested_tags(self):
        """italicized lines followed by linebreak and regular text."""
        expected = ("this is line 1 \r\n<i>italicized <b>this is bold and italics</b></i>\r\nno italics last line")
        els = self.dfxp.get_subtitles()
        self.assertEqual(expected, 
                         self.dfxp.get_content_with_markup(els[7], 
                         mappings=SRTGenerator.MAPPINGS))
