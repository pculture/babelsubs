from unittest import TestCase
from babelsubs import load_from
from babelsubs.generators.html import HTMLGenerator
from babelsubs.tests import utils


class HTMLGeneratorTest(TestCase):
    def setUp(self):
        subs  = utils.get_subs("simple.srt")
        self.parsed = subs.to_internal()
        self.subtitles = self.parsed.subtitles

    def assertText(self, text, index):
        self.assertIn(text, self.subtitles[index].text)

    # TODO: figure out if we really need to use em and strong, or if we can just make sure to
    #       normalize them into i and b
    def test_bold(self):
        self.assertText("We started <b>Universal Subtitles</b> because we believe", 0)

    def test_italics(self):
        self.assertText("Videomakers and websites should <i>really</i> care about this stuff too.", 3)

    def test_line_breaks(self):
        self.assertText("and then type along with the dialog<br>to create the subtitles", 7)

    def test_bad_input(self):
        # script tag should be gone
        self.assertText("the video can help make it more accessible.alert", 18)

class HTMLMappingsTest(TestCase):
    def test_escape(self):
        subs = utils.get_subs("simple.dfxp").to_internal()
        self.assertEquals(subs.subtitles[75].text, 'alert')

