from lxml import etree
from babelsubs.utils import unescape_html
from babelsubs.parsers.base import BaseTextParser, register
from babelsubs.storage import SubtitleSet


class YoutubeParser(BaseTextParser):

    file_type = 'youtube'

    def __init__(self, input_string, language_code):
        self.language_code = language_code
        self._pattern = None

        self.input_string = input_string
        self.language = language_code

    def to_internal(self):
        if not hasattr(self, 'sub_set'):
            self.sub_set = SubtitleSet(self.language)
            xml = etree.fromstring(self.input_string.encode('utf-8'))

            for item in xml:
                start = int(float(item.get('start')) * 1000)
                duration = int(float(item.get('dur')) * 1000)
                end = start + duration
                text = item.text and unescape_html(item.text) or u''
                self.sub_set.append_subtitle(start, end, text)

        return self.sub_set


register(YoutubeParser)
