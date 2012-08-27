import re

from babel import generators

class BaseParser(object):

    def __init__(self, subtitles, pattern, language=None, flags=[]):
        self.subtitles = subtitles
        self.pattern = pattern
        self.language = language
        self._pattern = re.compile(pattern, *flags)

    def __iter__(self):
        return self._result_iter()

    def __len__(self):
        return len(self._pattern.findall(self.subtitles))

    def __nonzero__(self):
        return bool(self._pattern.search(self.subtitles))

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
            yield self._get_data(item)

    def _get_data(self, match):
        return match.groupdict()

    def _get_matches(self):
        return self._pattern.finditer(self.subtitles)

    @classmethod
    def parse(cls, subtitles, language=None):
        return cls(subtitles, language)

    def to(self, type):
        generator = generators.discover(type)

        if not generator:
            raise TypeError("Could not find a type %s" % type)

        return generator.generate(self._result_iter(), language=self.language)

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
