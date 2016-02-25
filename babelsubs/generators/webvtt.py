from cgi import escape

from babelsubs.generators.base import BaseGenerator, register
from babelsubs.utils import UNSYNCED_TIME_FULL


class WEBVTTGenerator(BaseGenerator):
    file_type = 'vtt'

    MAPPINGS = dict(linebreaks="\n", bold="<b>%s</b>",
                    italics="<i>%s</i>", underline="<u>%s</u>",
                    quote_text=escape)

    def __init__(self, subtitle_set, language=None):
        super(WEBVTTGenerator, self).__init__(subtitle_set, language)
        self.line_delimiter = '\n'

    def __unicode__(self):
        output = ['WEBVTT\n']
        for from_ms, to_ms, content, meta in self.subtitle_set.subtitle_items(mappings=self.MAPPINGS):
            if meta['new_paragraph']:
                output.append(u'NOTE Paragraph')
                output.append(u'')

            output.append(u'%s --> %s' % (
                self.format_time(from_ms),
                self.format_time(to_ms)
            ))
            output.append(content)
            output.append(u'')
        return self.line_delimiter.join(output)[:-1]

    def format_time(self, milliseconds):
        if milliseconds is None:
            milliseconds = UNSYNCED_TIME_FULL

        seconds, milliseconds = divmod(int(milliseconds), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return u"%02i:%02i:%02i.%03i" % (hours, minutes, seconds, milliseconds)


register(WEBVTTGenerator)
