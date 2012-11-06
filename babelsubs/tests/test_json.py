from unittest2 import TestCase

from babelsubs.generators.json_generator import JSONGenerator
from babelsubs import SubtitleParserError
from babelsubs.parsers.json_parser import JSONParser
from babelsubs.tests import utils
import json


class JSONGeneratorTest(TestCase):

    def test_basic(self):
        subs = utils.get_subs("simple.srt")
        self.assertEquals(len(subs), 19)

        json_subs = JSONGenerator.generate(subs.to_internal())
        json_subs = json.loads(json_subs)

        self.assertEquals(len(json_subs), 19)

class JSONParserTest(TestCase):
    def test_invalid(self):
        with self.assertRaises(SubtitleParserError):
            JSONParser ("this\n\nisnot a valid subs format","en")

