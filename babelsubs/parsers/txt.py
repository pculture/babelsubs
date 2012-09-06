import re
from babelsubs import utils
from base import BaseTextParser, register
from babelsubs.storage import SubtitleSet

class TXTParser(BaseTextParser):

    file_type = 'txt'

    _linebreak_re = re.compile(r"\n\n|\r\n\r\n|\r\r")

    def __init__(self, input_string, language=None, linebreak_re=_linebreak_re):
        self.language = language
        self.input_string = linebreak_re.split(input_string)

    def __len__(self):
        return len(self.input_string)

    def __nonzero__(self):
        return bool(self.input_string)

    def _result_iter(self):
        for item in self.input_string:
            output = {}
            output['start'] = -1
            output['end'] = -1
            output['text'] = utils.strip_tags(item)
            yield output

    def to_internal(self):
        if not hasattr(self, 'sub_set'):
            self.sub_set = SubtitleSet(self.language)
            for item in self._result_iter():
                self.sub_set.append_subtitle(item['start'], item['end'], item['text'])
        return self.sub_set

register(TXTParser)
