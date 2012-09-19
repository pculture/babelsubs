# encoding: utf-8
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs.tests import utils
from babelsubs.generators.ssa import SSAGenerator
from babelsubs.parsers.ssa import SSAParser

class SSAParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.ssa")
        self.assertEquals(len(subs), 19)

    def test_self_generate(self):
        from ipdb import set_trace; set_trace()
        parsed_subs1 = utils.get_subs("simple.ssa")
        parsed_subs2 = SSAParser(unicode(parsed_subs1), 'en')

        for x1, x2 in zip([x for x in  parsed_subs1.to_internal()], [x for x in parsed_subs2.to_internal()]):
            self.assertEquals(x1, x2)

    def test_formatting(self):
        subs = """[Script Info]
Title: 
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.04,0:00:02.93,Default,,0000,0000,0000,,We started {\\b1}Universal Subtitles{\\b0} {\i1}because{\i0} we {\u1}believe{\u0}
"""
        parsed = SSAParser(subs, 'en')
        internal = parsed.to_internal()

        self.assertEquals(len(parsed), 1)
        element = internal.get_subtitles()[0]

        self.assertEquals(len(element.getchildren()), 3)
        bold, italics, underline = element.getchildren()

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

        output = unicode(SSAGenerator(internal))
        parsed2 = SSAParser(output, 'en')
        internal2 = parsed2.to_internal()

        for x1, x2 in zip([x for x in internal.subtitle_items(SSAGenerator.MAPPINGS)], \
                [x for x in internal2.subtitle_items(SSAGenerator.MAPPINGS)]):
            self.assertEquals(x1, x2)

