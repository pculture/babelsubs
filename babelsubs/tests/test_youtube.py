from unittest2 import TestCase

from babelsubs.parsers.youtube import YoutubeParser
from babelsubs.tests import utils


class YouTubeParsingTest(TestCase):

    def _get_subs(self, filename):
        return YoutubeParser(open(utils.get_data_file_path(filename)).read(), 'en').to_internal()

    def test_basic(self):
        subs  = self._get_subs("youtube.xml")
        self.assertEquals(len(subs), 31)
        
    def test_no_duration(self):
        subs  = self._get_subs("youtube-no-end.xml")
        sub_data = [x for x in subs.subtitle_items()]
        self.assertEquals(sub_data[0].start_time, 430)
        self.assertEquals(sub_data[0].end_time, 3170)
        # make sure the logic is right up to the last one
        self.assertEquals(sub_data[78].end_time, 210370)
        # last one should be hard coded to last 3 seconds
        self.assertEquals(sub_data[79].end_time, 213370)

