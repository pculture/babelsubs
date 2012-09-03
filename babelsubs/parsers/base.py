import re
from babelsubs.storage import SubtitleSet


class BaseTextParser(object):

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

    def __unicode__(self):
        return self.to(self.file_type)

    @classmethod
    def parse(cls, subtitles, language=None):
        return cls(subtitles, language)

    def to(self, type):
        from babelsubs import to
        return to(self.to_internal(), type, language=self.language)

    def to_internal(self):
        if not hasattr(self, 'sub_set'):
            self.sub_set = SubtitleSet(self.language)
            for match in self._matches:
                item = self._get_data(match)
                # fix me: support markup
                self.sub_set.append_subtitle(item['start'], item['end'], item['text']) 

        return self.sub_set

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
