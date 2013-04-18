import re
from babelsubs.storage import SubtitleSet


class BaseTextParser(object):
    # xml based formats must let encoding handling to the xml parser
    # as the encoding will be declared on the root el. All other
    # parsers should allow unicode
    NO_UNICODE = False

    def __init__(self, input_string, pattern, language=None, flags=[], eager_parse=True):
        '''
        If `eager_parse` is True will parse the subtitles right way, converting to our
        internal storage format, else only if you call `to_internal` directly (or `to`).
        Any errors during parsing will be of SubtitleParserError.
        Note that a file with no valid subs will be an error.
        '''
        self.input_string = input_string
        self.pattern = pattern
        self.language = language
        self._pattern = re.compile(pattern, *flags)
        if eager_parse:
            self.to_internal()

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
        if not isinstance(self.input_string, unicode) and not self.NO_UNICODE:
            self.input_string = self.input_string.decode('utf-8')
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
            match = None
            try:
                self.sub_set = SubtitleSet(self.language)
                for match in self._matches:
                    item = self._get_data(match.groupdict())
                    text = self.get_markup(item['text'])
                    self.sub_set.append_subtitle(item['start'], item['end'], text, escape=False)
                if match is None:
                    raise ValueError("No subs found")
            except Exception as e:
                raise SubtitleParserError(original_error=e)

        return self.sub_set

    def get_markup(self, text):
        return text.replace("\n", '<br/>')

    _matches = property(_get_matches)

class ParserListClass(dict):
    def register(self, parser):
        file_type = parser.file_type

        if isinstance(file_type, list):
            for ft in file_type:
                self[ft.lower()] = parser
        else:
            self[file_type] = parser

    def __getitem__(self, item):
        return super(ParserListClass, self).__getitem__(item.lower())

ParserList = ParserListClass()

class SubtitleParserError(Exception):
    '''
    Any error occurring during parsing will be of this type.
    The original error will be stored in 'original_error' to
    ease debugging.
    '''
    def __init__(self, *args, **kwargs):
        self.original_error = kwargs.pop("original_error", None)
        super(SubtitleParserError, self).__init__(*args, **kwargs)

def register(parser):
    ParserList.register(parser)

def discover(type):
    return ParserList[type]
