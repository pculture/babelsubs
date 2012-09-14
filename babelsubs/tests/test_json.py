try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs.generators.json_generator import JSONGenerator
from babelsubs.tests import utils
import json


class JSONGeneratorTest(TestCase):

    def test_basic(self):
        subs = utils.get_subs("simple.srt")
        self.assertEquals(len(subs), 19)

        json_subs = JSONGenerator.generate(subs.to_internal())
        json_subs = json.loads(json_subs)

        self.assertEquals(len(json_subs), 19)
