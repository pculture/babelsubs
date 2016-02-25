from cgi import escape
from babelsubs.generators.base import BaseGenerator, register
import json


class JSONGenerator(BaseGenerator):
    """
    [
        {
            "start": 39667,
            "end": 40300,
            "text": "Hello there",
            "position": 1
        },
        ...
    ]
    """
    file_type = 'json'

    MAPPINGS = dict(linebreaks="<br>", bold="<b>%s</b>",
                    italics="<i>%s</i>", underline="<u>%s</u>",
                    quote_text=escape)

    def __unicode__(self):
        output = []
        # FIXME: allow formatting tags
        i = 1
        for from_ms, to_ms, content, meta in self.subtitle_set.subtitle_items(mappings=self.MAPPINGS):
            output.append({
                'start': from_ms,
                'end': to_ms,
                'text': content,
                'position': i,
                'meta': meta
            })
            i += 1
        return json.dumps(output)


register(JSONGenerator)
