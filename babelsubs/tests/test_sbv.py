from unittest import TestCase

from babelsubs.generators.sbv import SBVGenerator
from babelsubs.parsers.sbv import SBVParser

from babelsubs.tests import utils
from babelsubs.storage import  SubtitleSet

class SBVParsingTest(TestCase):
    def setUp(self):
        self.subtitle_set = SubtitleSet('en')
        for x in xrange(0,5):
            self.subtitle_set.append_subtitle(x, x+1, unicode(x))

    def test_basic(self):
        subs  = utils.get_subs("simple.sbv")
        self.assertEquals(len(subs), 19)

    def test_unsyced_parsing(self):
        subs  = utils.get_subs("Untimed_text.sbv")
        self.assertEquals(len(subs), 43)

    def test_internal_format(self):
        subs  = utils.get_subs("simple.sbv")
        parsed = subs.to_internal()
        self.assertEquals(parsed.subtitles[0].start_time, 48)
        self.assertEquals(parsed.subtitles[0].end_time, 2932)
        self.assertEquals(parsed.subtitles[0].text, 'We started Universal Subtitles because we believe')

    def test_parsing_line_breaks(self):
        subs  = utils.get_subs("simple.sbv")
        parsed = subs.to_internal()
        self.assertEquals(parsed.subtitles[13].text,
                          'We support videos on <br>YouTube, Blip.TV, Ustream, and many more.')

    def test_generating_line_breaks(self):
        subtitle_set = SubtitleSet('en')
        subtitle_set.append_subtitle(0, 1000, "We support videos on <br>YouTube, Blip.TV, and more")
        generated = unicode(SBVGenerator(subtitle_set))
        # text is separated from timing by a carriage return
        self.assertEquals(generated.split('\r\n')[1],
                          "We support videos on [br]YouTube, Blip.TV, and more")

    def test_with_information_headers(self):
        # we ignore those headers for now, but at least we shouldn't fail on them
        subs  = utils.get_subs("with-information-header.sbv")
        parsed = subs.to_internal()
        self.assertEquals(parsed.subtitles[0][0], 48)
        self.assertEquals(parsed.subtitles[0][1], 2932)
        self.assertEquals(parsed.subtitles[0][2], 'We started Universal Subtitles because we believe')

    def test_round_trip(self):
        subs1  = utils.get_subs("simple.sbv")
        parsed1 = subs1.to_internal()
        output = unicode(SBVGenerator(parsed1))
        subs2  = SBVParser(output, 'en')
        parsed2 = subs2.to_internal()
        self.assertEquals(len(subs1), len(subs2))
        for x1, x2 in zip(parsed1.subtitles, parsed2.subtitles):
            self.assertEquals(x1, x2)

    def test_unsynced_generator(self):
        subs = SubtitleSet('en')
        for x in xrange(0,5):
            subs.append_subtitle(None, None, unicode(x))
        output = unicode(SBVGenerator(subs, language='en' ))

        parsed = SBVParser(output,'en')
        internal = parsed.to_internal()

        self.assertEqual(len(internal), 5)
        for i, subtitle in enumerate(internal.subtitles):
            self.assertEqual(subtitle[0], None)
            self.assertEqual(subtitle[1], None)

        generated = SBVGenerator(internal)
        self.assertEqual(generated.format_time(None), u'9:59:59.000')
        self.assertIn(u'''9:59:59.000,9:59:59.000\r\n0\r\n\r\n9:59:59.000,9:59:59.000\r\n1\r\n\r\n9:59:59.000,9:59:59.000\r\n2\r\n\r\n9:59:59.000,9:59:59.000\r\n3\r\n\r\n9:59:59.000,9:59:59.000\r\n4\r\n''',
            unicode(generated))

