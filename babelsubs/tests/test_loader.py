import re
from unittest import TestCase

from babelsubs import loader
from babelsubs.storage import SubtitleSet
from babelsubs.tests import utils

class TestLoader(TestCase):
    def setUp(self):
        self.loader = loader.SubtitleLoader()

    def test_create_new(self):
        subtitle_set = self.loader.create_new('en', 'title', 'description')
        self.assertEquals(subtitle_set.language_code, 'en')
        self.assertEquals(subtitle_set.title, 'title')
        self.assertEquals(subtitle_set.description, 'description')
        self.assertEquals(len(subtitle_set.subtitles), 0)

    def test_load(self):
        subtitle_set = self.loader.load('en', utils.get_data_file_path("simple.srt"))
        self.assertEquals(len(subtitle_set.subtitles), 19)
        self.assertEquals(subtitle_set.subtitles[0].start_time, 4)
        self.assertEquals(subtitle_set.subtitles[0].end_time, 2093)
        self.assertEquals(subtitle_set.subtitles[0].text,
                          'We started <b>Universal Subtitles</b> because we believe')

    def test_load_from_string(self):
        content = open(utils.get_data_file_path("simple.srt")).read()
        subtitle_set = self.loader.loads('en', content, 'srt')
        self.assertEquals(len(subtitle_set.subtitles), 19)
        self.assertEquals(subtitle_set.subtitles[0].start_time, 4)
        self.assertEquals(subtitle_set.subtitles[0].end_time, 2093)
        self.assertEquals(subtitle_set.subtitles[0].text,
                          'We started <b>Universal Subtitles</b> because we believe')
