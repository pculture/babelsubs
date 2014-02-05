from unittest2 import TestCase
from babelsubs import load_from
from babelsubs.generators.html import HTMLGenerator
from babelsubs.tests import utils


class HTMLGeneratorTest(TestCase):
    def setUp(self):
        subs  = utils.get_subs("simple.srt")
        self.parsed = subs.to_internal()
        self.sub_data = [x for x in self.parsed.subtitle_items(HTMLGenerator.MAPPINGS)]

    def assertText(self, text, sub_index):
        self.assertIn(text, self.sub_data[sub_index].text)

    def test_bold(self):
        self.assertText("We started <strong>Universal Subtitles</strong> because we believe", 0)

    def test_italics(self):
        self.assertText("Videomakers and websites should <em>really</em> care about this stuff too.", 3)

    def test_line_breaks(self):
        self.assertText("and then type along with the dialog<br>to create the subtitles", 7)

    def test_bad_input(self):
        # script tag should be gone
        self.assertText("the video can help make it more accessible.alert", 18)

class HTMLMappingsTest(TestCase):
    def test_escape(self):
        subs = utils.get_subs("simple.dfxp").to_internal()
        items = subs.subtitle_items(HTMLGenerator.MAPPINGS)
        self.assertEquals(items[75].text,
                          '&lt;script&gt;alert&lt;/script&gt;')

