import re
from babelsubs import utils
from base import BaseTextParser, register, SubtitleParserError
from babelsubs.storage import SubtitleSet

class TXTParser(BaseTextParser):

    file_type = 'txt'

    _linebreak_re = re.compile(r"\n\n|\r\n\r\n|\r\r")

    def __init__(self, input_string, language=None, linebreak_re=_linebreak_re, eager_parse=True):
        self.language = language
        self.input_string = linebreak_re.split(input_string)

        if eager_parse:
            self.to_internal()

    def __len__(self):
        return len(self.input_string)

    def __nonzero__(self):
        return bool(self.input_string)

    def _result_iter(self):
        for item in self.input_string:
            output = {}
            output['start'] = None
            output['end'] = None
            output['text'] = utils.strip_tags(item)
            yield output

    def to_internal(self):

        if not hasattr(self, 'sub_set'):
            self.sub_set = SubtitleSet(self.language)
            valid = False
            for item in self._result_iter():
                item['text'] = item['text'].replace("\n", '<br/>')
                if not valid and ''.join(item['text'].split()):
                    valid = True
                self.sub_set.append_subtitle(item['start'], item['end'],
                                             item['text'], escape=False)
            if not valid:
                raise SubtitleParserError("No subs")
        return self.sub_set


register(TXTParser)
