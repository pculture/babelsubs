from lxml import etree
from babelsubs.utils import unescape_html
from babelsubs.parsers.base import BaseTextParser, register, SubtitleParserError
from babelsubs.storage import SubtitleSet


class YoutubeParser(BaseTextParser):

    file_type = 'youtube'

    def __init__(self, input_string, language_code):
        self.language_code = language_code
        self._pattern = None

        self.input_string = input_string
        self.language = language_code

    def __iter__(self):
        if not hasattr(self, 'sub_set'):
            self.to_internal()

        for sub in self.sub_set:
            yield sub

    def to_internal(self):
        if not hasattr(self, 'sub_set'):
            try:
                self.sub_set = SubtitleSet(self.language)
                xml = etree.fromstring(self.input_string.encode('utf-8'))

                has_subs = False
                total_items = len(xml)
                for i,item in enumerate(xml):
                    duration = 0
                    start = int(float(item.get('start')) * 1000)
                    if hasattr(item, 'duration'):
                        duration = int(float(item.get('dur', 0)) * 1000)
                    elif i+1 < total_items:
                        # youtube sometimes omits the duration attribute
                        # in this case we're displaying until the next sub
                        # starts
                        next_item = xml[i+1]
                        duration = int(float(next_item.get('start')) * 1000) - start
                    else:
                        # hardcode the last sub duration at 3 seconds
                        duration = 3000
                    end = start + duration
                    text = item.text and unescape_html(item.text) or u''
                    self.sub_set.append_subtitle(start, end, text)
                    has_subs = True
                if not has_subs:
                    raise ValueError("No subs")
            except Exception as e:
                raise SubtitleParserError(original_error=e)


        return self.sub_set


register(YoutubeParser)
