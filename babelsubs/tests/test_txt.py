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

    def check_parsing(self, content, correct_subs):
        subtitles = TXTParser.parse(content).to_internal().subtitle_items(
            mappings=TXTGenerator.MAPPINGS)
        self.assertEqual([s.text for s in subtitles], correct_subs)
        for sub in subtitles:
            self.assertEqual(sub.start_time, None)
            self.assertEqual(sub.end_time, None)

    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            TXTParser("\n\n","en")

    def test_linebreak(self):
        self.check_parsing("one\ntwo", ["one\ntwo"])

    def test_double_linebreak_starts_new_sub(self):
        self.check_parsing("one\n\ntwo", ["one", "two"])

class TXTGeneraorTest(TestCase):

    def test_linebreaks(self):
        sset = SubtitleSet('en')
        sset.append_subtitle(0, 1000, '''line 1<br />line 2<br />line 3''',
                             escape=False)
        sset.append_subtitle(1000,200, 'second sub')
        output = unicode(TXTGenerator(sset))
        self.assertEqual(output, TXT_LINEBREAKS)
