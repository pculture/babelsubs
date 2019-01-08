import unittest
from unittest import TestCase

from babelsubs import storage
from babelsubs.generators.html import HTMLGenerator
from babelsubs.generators.srt import SRTGenerator
from babelsubs.parsers import SubtitleParserError
from babelsubs.tests import utils
from babelsubs import utils as main_utils

class AddSubtitlesTest(TestCase):
    def test_new_paragraph(self):
        subtitle_set = storage.SubtitleSet('en')
        subtitle_set.append_subtitle(0, 1000, "paragraph 1 - A")
        subtitle_set.append_subtitle(1000, 2000, "paragraph 1 - B")
        subtitle_set.append_subtitle(2000, 3000, "paragraph 2 - A", new_paragraph=True)
        subtitle_set.append_subtitle(3000, 4000, "paragraph 2 - B", new_paragraph=False)
        subtitle_set.append_subtitle(3000, 4000, "paragraph 2 - C")

        subtitles = subtitle_set.subtitles
        # make sure subtitle items returns the right metadata
        self.assertFalse(subtitles[1].new_paragraph)
        self.assertTrue(subtitles[2].new_paragraph)
        self.assertFalse(subtitles[3].new_paragraph)

    def test_no_timing(self):
        subtitle_set = storage.SubtitleSet('en')
        subtitle_set.append_subtitle(0, 1000, "paragraph 1 - A")
        subtitle_set.append_subtitle(2000, None, "paragraph 1 - B")
        subtitle_set.append_subtitle(None, None, "paragraph 1 - C")
        subtitles = subtitle_set.subtitles
        self.assertEquals(len(subtitles), 3)
        self.assertEquals(subtitles[0].start_time, 0)
        self.assertEquals(subtitles[0].end_time, 1000)
        self.assertEquals(subtitles[1].start_time, 2000)
        self.assertEquals(subtitles[1].end_time, None)
        self.assertEquals(subtitles[2].start_time, None)
        self.assertEquals(subtitles[2].end_time, None)
        self.assertFalse(subtitle_set.fully_synced)
        subtitle_set = storage.SubtitleSet('en')
        subtitle_set.append_subtitle(0, 1000, "paragraph 1 - A")
        subtitle_set.append_subtitle(1000, 2000, "paragraph 1 - B")
        subtitle_set.append_subtitle(2000, 3000, "paragraph 2 - A", new_paragraph=True)
        subtitle_set.append_subtitle(3000, 4000, "paragraph 2 - B")
        subtitle_set.append_subtitle(3000, 4000, "paragraph 2 - C")
        self.assertTrue(subtitle_set.fully_synced)

    def test_escaping(self):
        subtitle_set= storage.SubtitleSet('en')
        subtitle_set.append_subtitle(0, 1000, "Hey <alert><a><i>html</i> <b>anchor</b></a></alert>")
        self.assertEqual(subtitle_set.subtitles[0].text, 'Hey <i>html</i> <b>anchor</b>')
        
    def test_paragraph_from_list(self):
        subs = []
        for x in xrange(0,10):
            subs.append((x * 1000, x * 1000 + 999, "Sub {}".format(x), {'new_paragraph': x % 2 == 0}))

        subtitle_set = storage.SubtitleSet.from_list('en', subs)
        self.assertEqual(len(subtitle_set.subtitles), 10)
        for i, subtitle in enumerate(subtitle_set.subtitles):
            self.assertEqual(subtitle.new_paragraph, (i % 2 == 0))  # test if every other is True

    def test_control_chars_from_list(self):
        subs = [
            # normal sub
            (1000,  1100, "Sub 1", {'new_paragraph': True}),
            # sub with an invalid control char
            (2000,  2100, "Sub 2\x15", {'new_paragraph': False}),
        ]
        subtitle_set = storage.SubtitleSet.from_list('en', subs)
        self.assertEquals(subtitle_set.subtitles[0].text, u'Sub 1')
        self.assertEquals(subtitle_set.subtitles[1].text, u'Sub 2')

    def test_region(self):
        subs = storage.SubtitleSet('en')
        subs.append_subtitle(0, 1000, "test", region="top")
        self.assertEqual(subs.subtitles[0].region, 'top')
