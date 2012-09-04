try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs.parsers.dfxp import DFXPParser
from babelsubs.generators.dfxp import DFXPGenerator

from babelsubs.tests import utils
from babelsubs import load_from


class DFXPParsingTest(TestCase):

    def test_basic(self):
        subs  = utils.get_subs("simple.dfxp")
        self.assertEquals(len(subs), 76)
        
    def test_internal_format(self):
        subs  = utils.get_subs("simple.dfxp")
        parsed = subs.to_internal()
        sub_data = [x for x in parsed.subtitle_items()]
        self.assertEquals(sub_data[0][0], 1200)
        self.assertEquals(sub_data[0][1], 4467)
        self.assertEquals(sub_data[3][2], 'at least 7,000 years ago.')

    def test_self_generate(self):
        parsed_subs1 = utils.get_subs("simple.dfxp")
        parsed_subs2 = DFXPParser(DFXPGenerator(parsed_subs1.subttitle_set, 'en').__unicode__())

        for x1, x2 in zip([x for x in  parsed_subs1.to_internal()], [x for x in parsed_subs2.to_internal()]):
            self.assertEquals(x1, x2)

    def test_load_from_string(self):
        filename = utils.get_data_file_path('simple.dfxp')
        with open(filename) as f:
            s = f.read()
        load_from(s, type='dfxp').to_internal()
