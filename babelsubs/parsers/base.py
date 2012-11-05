import re
from babelsubs.storage import SubtitleSet


class BaseTextParser(object):

    def __init__(self, input_string, pattern, language=None, flags=[]):
        self.input_string = input_string
        self.pattern = pattern
        self.language = language
        self._pattern = re.compile(pattern, *flags)

    def __iter__(self):
        return self._result_iter()

    def __len__(self):
        return len(self._pattern.findall(self.input_string))

    def __nonzero__(self):
        return bool(self._pattern.search(self.input_string))

    def _result_iter(self):
        """
        Should iterate over items like this:
        {
            'start': ...,
            'end': ...,
            'text': ...
        }
        start_time and end_time in seconds. If it is not defined use -1.
        """
        for item in self._matches:
            yield self._get_data(item.groupdict())

    def _get_data(self, match):
        return match

    def _get_matches(self):
        return self._pattern.finditer(self.input_string)

    def __unicode__(self):
        return self.to(self.file_type)

    @classmethod
    def parse(cls, input_string, language=None):
        return cls(input_string, language)

    def to(self, type):
        from babelsubs import to
        if isinstance(type, list):
            type = type[0]

        return to(self.to_internal(), type, language=self.language)

    def to_internal(self):
        if not hasattr(self, 'sub_set'):
            self.sub_set = SubtitleSet(self.language)
            for match in self._matches:
                item = self._get_data(match.groupdict())
                # fix me: support markup
                text = self.get_markup(item['text'])
                self.sub_set.append_subtitle(item['start'], item['end'], text, escape=False)

        return self.sub_set

    def get_markup(self, text):
        return text

    _matches = property(_get_matches)

class ParserListClass(dict):
    def register(self, parser):
        file_type = parser.file_type

        if isinstance(file_type, list):
            for ft in file_type:
                self[ft] = parser
        else:
            self[file_type] = parser

    def __getitem__(self, item):
        return self.get(item, None)

ParserList = ParserListClass()

class SubtitleParserError(Exception):
    pass

def register(parser):
    ParserList.register(parser)

def discover(type):
    return ParserList[type]
