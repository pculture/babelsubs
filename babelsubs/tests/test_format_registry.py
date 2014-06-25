from unittest2 import TestCase
from babelsubs import get_available_formats
from babelsubs.parsers import base, discover
from babelsubs.parsers.base import ParserList
from babelsubs.generators.base import GeneratorList
from babelsubs.generators.base import discover as generator_discover


class FormatRegistryTest(TestCase):
    def test_parsing_discover_lowercase(self):
        self.assertTrue(base.ParserList['srt'])
        self.assertTrue(base.ParserList['SRT'])
        self.assertTrue(discover('srt'))
        self.assertTrue(discover('SRT'))

    def test_parsing_discover_missing(self):
        with self.assertRaises(KeyError):
            ParserList['badformat']
        with self.assertRaises(KeyError):
            discover('badformat')

    def test_generator_discover_lowercase(self):
        self.assertTrue(GeneratorList['srt'])
        self.assertTrue(GeneratorList['SRT'])
        self.assertTrue(generator_discover('srt'))
        self.assertTrue(generator_discover('SRT'))


    def test_generating_discover_missing(self):
        with self.assertRaises(KeyError):
            GeneratorList['badformat']
        with self.assertRaises(KeyError):
            generator_discover('badformat')

    def test_dfxp_aliases(self):
        self.assertTrue(discover('xml'))

