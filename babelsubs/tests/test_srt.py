try:
    from unittest2 import TestCase
except ImportError:
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
        sub_data = [x for x in parsed.subtitle_items(SRTGenerator.MAPPINGS)]
        self.assertEquals(sub_data[0][0], 4)
        self.assertEquals(sub_data[0][1], 2093)
        self.assertEquals(sub_data[0][2], "We started <b>Universal Subtitles</b> because we believe")

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
        
    def test_self_generate(self):
        parsed_subs1 = utils.get_subs("simple.srt")
        parsed_subs2 = SRTParser(unicode(parsed_subs1), 'en')

        for x1, x2 in zip([x for x in  parsed_subs1.to_internal()], [x for x in parsed_subs2.to_internal()]):
            self.assertEquals(x1, x2)

    def test_formatting(self):
        subs = u"""1
00:00:00,004 --> 00:00:02,093
We\n started <b>Universal Subtitles</b> <i>because</i> we <u>believe</u>
"""
        parsed = SRTParser(subs, 'en')
        internal = parsed.to_internal()

        self.assertEquals(len(parsed), 1)
        element = internal.get_subtitles()[0]

        self.assertTrue(len(element.getchildren()), 3)
        br, bold, italics, underline = element.getchildren()

        self.assertEquals(br.text, None)
        self.assertEquals(' started ', br.tail)
        self.assertEquals(br.tag, '{http://www.w3.org/ns/ttml}br')

        self.assertEquals(bold.text, 'Universal Subtitles')
        self.assertEquals(bold.tail, ' ')
        self.assertEquals(bold.tag, '{http://www.w3.org/ns/ttml}span')
        self.assertIn('fontWeight', bold.attrib)
        self.assertEquals(bold.attrib['fontWeight'], 'bold')

        self.assertEquals(italics.text, 'because')
        self.assertEquals(italics.tail, ' we ')
        self.assertEquals(italics.tag, '{http://www.w3.org/ns/ttml}span')
        self.assertIn('fontStyle', italics.attrib)
        self.assertEquals(italics.attrib['fontStyle'], 'italic')

        self.assertEquals(underline.text, 'believe')
        self.assertEquals(underline.tail, None)
        self.assertEquals(underline.tag, '{http://www.w3.org/ns/ttml}span')
        self.assertIn('textDecoration', underline.attrib)
        self.assertEquals(underline.attrib['textDecoration'], 'underline')

        output = unicode(SRTGenerator(internal))
        parsed2 = SRTParser(output, 'en')
        internal2 = parsed2.to_internal()

        for x1, x2 in zip([x for x in internal.subtitle_items(SRTGenerator.MAPPINGS)], \
                [x for x in internal2.subtitle_items(SRTGenerator.MAPPINGS)]):
            self.assertEquals(x1, x2)
