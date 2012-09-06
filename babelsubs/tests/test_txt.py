# encoding: utf-8
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs.parsers.txt import TXTParser


TXT_TEXT = u"""
Welkom bij de presentatie é over optellen niveau 2

And the message, with non ascii chars caçao.
"""


class TXTParsingTest(TestCase):

    def test_basic(self):
        subs = TXTParser.parse(TXT_TEXT.encode('utf-8'))
        self.assertEquals(len(subs), 2)
