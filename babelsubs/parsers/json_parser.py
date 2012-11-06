import json
from babelsubs.storage import SubtitleSet
from babelsubs.parsers.base import (
    BaseTextParser, register, SubtitleParserError
)


class JSONParser(BaseTextParser):
    file_type = 'json'

    def __init__(self, input_string, pattern, language=None, flags=[], eager_parse=True):
        self.input_string = input_string
        self.pattern = pattern
        self.language = language
        super(JSONParser, self).__init__(input_string, pattern, language=language,
            flags=[], eager_parse=eager_parse)

    def to_internal(self):
        if not hasattr(self, 'sub_set'):
            self.sub_set = SubtitleSet(self.language)

            try:
                data = json.loads(self.input_string)
            except ValueError:
                raise SubtitleParserError("Invalid JSON data provided.")

            # Sort by the ``position`` key
            data = sorted(data, key=lambda k: k['position'])

            for sub in data:
                self.sub_set.append_subtitle(sub['start'], sub['end'],
                    sub['text'])

        return self.sub_set


register(JSONParser)
