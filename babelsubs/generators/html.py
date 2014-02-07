from cgi import escape

from babelsubs.generators.base import BaseGenerator, register
from babelsubs.utils import UNSYNCED_TIME_FULL


class HTMLGenerator(BaseGenerator):
    file_type = 'html'

    MAPPINGS = dict(linebreaks="<br>", bold="<strong>%s</strong>",
        italics="<em>%s</em>", underline="<u>%s</u>", quote_text=escape)

    def __init__(self, subtitle_set, language=None):
        super(HTMLGenerator, self).__init__(subtitle_set, language)
        self.line_delimiter = '\r\n'

    def __unicode__(self):
        output = []
        i = 1
        for from_ms, to_ms, content, meta in self.subtitle_set.subtitle_items(mappings=self.MAPPINGS):
            output.append(unicode(i))
            output.append(u'%s --> %s' % (
                self.format_time(from_ms),
                self.format_time(to_ms)
                ))
            output.append(content)
            output.append(u'')
            i += 1
        return self.line_delimiter.join(output)

    def format_time(self, milliseconds):
        if milliseconds is None:
            milliseconds = UNSYNCED_TIME_FULL

        seconds, milliseconds = divmod(int(milliseconds), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return u"%02i:%02i:%02i,%03i" % (hours, minutes, seconds, milliseconds)


register(HTMLGenerator)
