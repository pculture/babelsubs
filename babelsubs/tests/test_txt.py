# encoding: utf-8
from unittest2 import TestCase

from babelsubs import SubtitleParserError
from babelsubs.parsers.txt import TXTParser


TXT_TEXT = u"""
Welkom bij de presentatie é over optellen niveau 2

And the message, with non ascii chars caçao.
"""


class TXTParsingTest(TestCase):

    def test_basic(self):
        subs = TXTParser.parse(TXT_TEXT.encode('utf-8'))
        self.assertEquals(len(subs), 2)
        [x for x in subs.to_internal().subtitle_items()]

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            TXTParser("\n\n","en")

