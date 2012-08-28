import re
from babelsubs import utils
from base import BaseParser, register

class TXTParser(BaseParser):

    file_type = 'txt'

    _linebreak_re = re.compile(r"\n\n|\r\n\r\n|\r\r")

    def __init__(self, subtitles, language=None, linebreak_re=_linebreak_re):
        self.subtitles = linebreak_re.split(subtitles, language)

    def __len__(self):
        return len(self.subtitles)

    def __nonzero__(self):
        return bool(self.subtitles)

    def _result_iter(self):
        for item in self.subtitles:
            output = {}
            output['start'] = -1
            output['end'] = -1
            output['text'] = utils.strip_tags(item)
            yield output

register(TXTParser)
