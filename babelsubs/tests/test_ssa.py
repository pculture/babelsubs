# encoding: utf-8
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs.parsers.ssa import SSAParser


SSA_TEXT = u'''
﻿[Script Info]
Title: Ambientes de alta concorrência: PostgreSQL Conf 2011
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.01,0:00:02.71,Default,,0000,0000,0000,,Welkom bij de presentatie é over optellen niveau 2
Dialogue: 0,0:00:02.71,9:59:59.00,Default,,0000,0000,0000,,And the message, with non ascii chars caçao.
'''


class SSAParsingTest(TestCase):

    def test_basic(self):
        subs = SSAParser.parse(SSA_TEXT)
        self.assertEquals(len(subs), 2)

        subs = SSAParser.parse(SSA_TEXT.encode('utf-8'))
        self.assertEquals(len(subs), 2)
