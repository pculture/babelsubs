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

    def check_ttml(self, ttml, language_code, title, description):
        self.assertEquals(ttml.nsmap, {
            None: TTML_NAMESPACE_URI,
            'tts': TTS_NAMESPACE_URI,
            'ttm': TTM_NAMESPACE_URI,
        })
        self.assertEquals(ttml.attrib, {
            XML + 'lang': language_code,
        })
        head = ttml.find(TTML + 'head')
        metadata = head.find(TTML + 'metadata')

        self.assertEquals(metadata.find(TTM + 'title').text, title)
        self.assertEquals(metadata.find(TTM + 'description').text,
                          description)

        styles = head.find(TTML + 'styling').findall(TTML + 'style')
        regions = head.find(TTML + 'layout').findall(TTML + 'region')
        self.assertEquals(len(styles), 1)
        self.assertEquals(styles[0].attrib, {
            XML + 'id': 'test-style',
            TTS + 'color': 'white',
            TTS + 'fontSize': '18px',
        })

        self.assertEquals(len(regions), 2)
        self.assertEquals(regions[0].attrib, {
            XML + 'id': 'bottom',
            TTML + 'style': 'test-style',
            TTS + 'extent': '100% 20%',
            TTS + 'origin': '0 80%',
        })
        self.assertEquals(regions[1].attrib, {
            XML + 'id': 'top',
            TTML + 'style': 'test-style',
            TTS + 'extent': '100% 20%',
            TTS + 'origin': '0 0',
        })

        self.assertEquals(ttml.find(TTML + 'body').attrib, {
            TTML + 'region': 'bottom',
        })

    def test_create_new(self):
        subs = self.loader.create_new('en', 'title', 'description')
        self.check_ttml(subs._ttml, 'en', 'title', 'description')
        self.assertEquals(len(subs.subtitle_items()), 0)

    def check_srt_import(self, subs):
        self.check_ttml(subs._ttml, 'en', '', '')

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
