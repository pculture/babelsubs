import re
from babelsubs import utils
from base import BaseTextParser, register

class TXTParser(BaseTextParser):

    file_type = 'txt'

    _linebreak_re = re.compile(r"\n\n|\r\n\r\n|\r\r")

    def __init__(self, input_string, language=None, linebreak_re=_linebreak_re):
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

register(TXTParser)
