from unittest2 import TestCase
from babelsubs import load_from, load_from_file
from babelsubs.tests import utils


class LoadFromTest(TestCase):
    def test_type_specified(self):
        subs = load_from_file(utils.get_data_file_path("simple.srt"), type='srt')
        parsed = subs.to_internal()
        self.assertEquals(len(parsed), 19)

    def test_type_guessing(self):
        subs = load_from_file(utils.get_data_file_path("simple.srt"))
        parsed = subs.to_internal()
        self.assertEquals(len(parsed), 19)

    def test_type_override(self):
        subs = load_from_file(utils.get_data_file_path("simple-srt.badextension"), type='srt')
        parsed = subs.to_internal()
        self.assertEquals(len(parsed), 19)

    def test_from_string(self):
        subs  = load_from(open(utils.get_data_file_path("simple-srt.badextension"), 'r').read() ,type='srt')
        parsed = subs.to_internal()
        self.assertEquals(len(parsed), 19)

    def test_from_string_requires_type(self):
        data = open(utils.get_data_file_path("simple-srt.badextension"), 'r').read()
        self.assertRaises(TypeError, load_from, data)



