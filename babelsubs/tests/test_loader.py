from lxml import etree
import re
from unittest2 import TestCase

from babelsubs import loader
from babelsubs.generators.dfxp import DFXPGenerator
from babelsubs.storage import SubtitleSet
from babelsubs.tests import utils
from babelsubs.xmlconst import *

class TestLoader(TestCase):
    def setUp(self):
        self.loader = loader.SubtitleLoader()
        self.loader.add_style('test-style', color='white', fontSize='18px')
        self.loader.add_region('bottom', 'test-style', extent='100% 20%', origin='0 80%')
        self.loader.add_region('top', 'test-style', extent='100% 20%', origin='0 0')

    def test_create_new(self):
        subs = self.loader.create_new('en', 'title', 'description')
        self.check_ttml_start(subs, 'en', 'title', 'description')
        self.assertEquals(len(subs.subtitle_items()), 0)

    def check_srt_import(self, subs):
        self.check_ttml_start(subs, 'en')

        divs = subs._ttml.find(TTML + 'body').findall(TTML + 'div')
        self.assertEquals(len(divs), 1)

        items = subs.subtitle_items()
        self.assertEquals(len(items), 19)
        self.assertEquals(items[0].start_time, 4)
        self.assertEquals(items[0].end_time, 2093)
        self.assertEquals(items[0].text,
                          'We started Universal Subtitles because we believe')

    def test_load(self):
        subs = self.loader.load('en', utils.get_data_file_path("simple.srt"))
        self.check_srt_import(subs)

    def test_load_from_string(self):
        content = open(utils.get_data_file_path("simple.srt")).read()
        subs = self.loader.loads('en', content, 'srt')
        self.check_srt_import(subs)

    def test_load_from_dfxp(self):
        subs = self.loader.load('en', utils.get_data_file_path("simple.dfxp"))
        # since we are loading directly from DFXP, we should keep the
        # styling/layout the same as the file

        head = subs._ttml.find(TTML + 'head')
        styling = head.find(TTML + 'styling')
        styles = styling.findall(TTML + 'style')
        self.assertEquals(len(styles), 1)
        self.assertEquals(styles[0].attrib, {
            'id': "defaultCaption",
            TTS + 'fontSize': "14px",
            TTS + 'fontFamily': "Arial",
            TTS + 'fontWeight': "normal",
            TTS + 'fontStyle': "normal",
            TTS + 'textDecoration': "none",
            TTS + 'color': "white",
            TTS + 'backgroundColor': "black",
            TTS + 'textAlign': "center",
        })

        self.assertEquals(head.find(TTML + 'layout'), None)

    def check_ttml_start(self, subs, language_code, title=None, description=None):
        top_part = re.match("(.*</head>)", subs.to_xml(), re.DOTALL)
        if title:
            title_tag = '<ttm:title>%s</ttm:title>' % (title,)
        else:
            title_tag = '<ttm:title></ttm:title>'
        if description:
            description_tag = ('<ttm:description>%s</ttm:description>' %
                               (description,))
        else:
            description_tag = '<ttm:description></ttm:description>'

        correct_start = """\
<tt xmlns:tts="http://www.w3.org/ns/ttml#styling" xmlns:ttm="http://www.w3.org/ns/ttml#metadata" xmlns="http://www.w3.org/ns/ttml" xml:lang="{language_code}">
    <head>
        <metadata>
            {title_tag}
            {description_tag}
            <ttm:copyright/>
        </metadata>
        <styling>
            <style xml:id="test-style" tts:color="white" tts:fontSize="18px"/>
        </styling>
        <layout>
            <region xml:id="bottom" style="test-style" tts:origin="0 80%" tts:extent="100% 20%"/>
            <region xml:id="top" style="test-style" tts:origin="0 0" tts:extent="100% 20%"/>
        </layout>
    </head>""".format(language_code=language_code, title_tag=title_tag,
                      description_tag=description_tag)
        utils.assert_long_text_equal(top_part.group(0), correct_start)

    def test_dfxp_merge(self):
        en_subs = SubtitleSet('en')
        es_subs = SubtitleSet('es')
        en_subs.append_subtitle(1000, 1500, 'content')
        es_subs.append_subtitle(1000, 1500, 'spanish content')
        result = self.loader.dfxp_merge([en_subs, es_subs])

        utils.assert_long_text_equal(result, """\
<tt xmlns:tts="http://www.w3.org/ns/ttml#styling" xmlns:ttm="http://www.w3.org/ns/ttml#metadata" xmlns="http://www.w3.org/ns/ttml" xml:lang="">
    <head>
        <metadata>
            <ttm:title></ttm:title>
            <ttm:description></ttm:description>
            <ttm:copyright/>
        </metadata>
        <styling>
            <style xml:id="test-style" tts:color="white" tts:fontSize="18px"/>
        </styling>
        <layout>
            <region xml:id="bottom" style="test-style" tts:origin="0 80%" tts:extent="100% 20%"/>
            <region xml:id="top" style="test-style" tts:origin="0 0" tts:extent="100% 20%"/>
        </layout>
    </head>
    <body region="bottom">
        <div xml:lang="en">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">content</p>
            </div>
        </div>
        <div xml:lang="es">
            <div>
                <p begin="00:00:01.000" end="00:00:01.500">spanish content</p>
            </div>
        </div>
    </body>
</tt>
""")
