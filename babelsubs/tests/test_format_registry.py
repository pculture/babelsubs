from unittest2 import TestCase
from babelsubs import get_available_formats
from babelsubs.parsers import base, discover


class FormatRegistryTest(TestCase):
    def test_available_formats(self):
        actual_formats = sorted(get_available_formats())
        expected_formats = sorted(['ass', 'ttml', 'srt', 'dfxp', 'ssa', 'sbv', 'txt', 'json', 'xml', 'youtube'])
        self.assertEqual(actual_formats, expected_formats)

    def test_discover_lowercase(self):
        self.assertTrue(base.ParserList['srt'])
        self.assertTrue(base.ParserList['SRT'])
        self.assertTrue(discover('srt'))
        self.assertTrue(discover('SRT'))


    def test_discover_missing(self):
        with self.assertRaises(KeyError):
            base.ParserList['badformat']
        with self.assertRaises(KeyError):
            discover('badformat')

