# encoding: utf-8
from unittest2 import TestCase

from babelsubs import SubtitleParserError
from babelsubs.tests import utils
from babelsubs.generators.ssa import SSAGenerator
from babelsubs.parsers.ssa import SSAParser
from babelsubs import storage

class SSAParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.ssa")
        self.assertEquals(len(subs), 19)

    def test_self_generate(self):
        parsed_subs1 = utils.get_subs("simple.ssa")
        generated = SSAParser(unicode(parsed_subs1), 'en')

        for x1, x2 in zip([x for x in  parsed_subs1.to_internal()], [x for x in generated.to_internal()]):
            self.assertEquals(x1, x2)

    def test_generate_centiseconds(self):
        sset = storage.SubtitleSet('en')
        sset.append_subtitle(133, 238,'hey')
        output = unicode(SSAGenerator(sset))
        # make sure time is 230 milliseconds not 38 and that
        # we are rounding to 0.24 (instead of truncating to 0.23
        self.assertIn("Dialogue: 0,0:00:00.13,0:00:00.24", output)

    def test_formatting(self):
        subs = """[Script Info]
Title: 
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.04,0:00:02.93,Default,,0000,0000,0000,,We\n started {\\b1}Universal Subtitles{\\b0} {\i1}because{\i0} we {\u1}believe{\u0}
"""
        parsed = SSAParser(subs, 'en')
        internal = parsed.to_internal()

        # make sure timming looks right
        subs = [x for x in internal.subtitle_items()]
        self.assertEqual(subs[0][0], 40)
        self.assertEqual(subs[0][1], 2930)
        self.assertEquals(len(parsed), 1)

        element = internal.get_subtitles()[0]

        #FIXME: when we implement proper parsing of formatting
        return
        self.assertEquals(len(element.getchildren()), 4)
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


    def test_timing_parser(self):
        parsed_subs = utils.get_subs("simple.ssa")
        subs = [a for a in parsed_subs.to_internal().subtitle_items()]
        self.assertEqual(subs[0][0], 40)
        self.assertEqual(subs[0][1], 2930)

    def test_timing_generator(self):
        sset = storage.SubtitleSet('en')
        sset.append_subtitle(40, 2930,"We started Universal Subtitles because we believe")
        generated = unicode(SSAGenerator(sset))
        self.assertIn('Dialogue: 0,0:00:00.04,0:00:02.93,Default,,0000,0000,0000,,We started Universal Subtitles because we believe', generated)

    def test_unsynced_generator(self):
        subs = storage.SubtitleSet('en')
        for x in xrange(0,5):
            subs.append_subtitle(None, None,"%s" % x)
        output = unicode(SSAGenerator(subs))

        parsed = SSAParser(output,'en')
        internal = parsed.to_internal()
        subs = [x for x in internal.subtitle_items()]
        self.assertEqual(len(internal), 5)
        for i,sub in enumerate(subs):
            self.assertEqual(sub[0], None )
            self.assertEqual(sub[1], None )
        generated = SSAGenerator(internal)
        self.assertEqual(generated.format_time(None), u'9:59:59.99')
        self.assertIn(u'Dialogue: 0,9:59:59.99,9:59:59.99,Default,,0000,0000,0000,,2', unicode(generated))

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            SSAParser ("this\n\nisnot a valid subs format","en")

