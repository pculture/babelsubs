# encoding: utf-8
from babelsubs import SubtitleParserError
from babelsubs.generators import TXTGenerator
from babelsubs.parsers.txt import TXTParser
from babelsubs.storage import SubtitleSet
from unittest2 import TestCase



TXT_TEXT = u"""
Welkom bij de presentatie é over optellen niveau 2

And the message, with non ascii chars caçao.
"""


TXT_LINEBREAKS = u'''line 1
line 2
line 3

second sub'''

class TXTParsingTest(TestCase):

    def test_basic(self):
        subs = TXTParser.parse(TXT_TEXT.encode('utf-8'))
        self.assertEquals(len(subs), 2)
        [x for x in subs.to_internal().subtitle_items()]

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            TXTParser("\n\n","en")

    def test_linebreaks(self):
        input_str = '''hey
        hey2
        hey3

        second line'''
        subs = TXTParser.parse(input_str)
        self.assertEqual(len(subs), 2)

class TXTGeneraorTest(TestCase):

    def test_linebreaks(self):
        sset = SubtitleSet('en')
        sset.append_subtitle(0, 1000, '''line 1
line 2
line 3''')
        sset.append_subtitle(1000,200, 'second sub')
        output = unicode(TXTGenerator(sset))
        self.assertEqual(output, TXT_LINEBREAKS)
