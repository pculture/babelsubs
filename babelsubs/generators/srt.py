from cgi import escape
from babelsubs.generators.base import BaseGenerator, register
from babelsubs.utils import UNSYNCED_TIME_FULL


class SRTGenerator(BaseGenerator):
    file_type = 'srt'

    def __init__(self, subtitle_set, language=None):
        super(SRTGenerator, self).__init__(subtitle_set, language)
        self.line_delimiter = '\n'

    def __unicode__(self):
        output = []
        i = 1
        for from_ms, to_ms, content, meta in self.subtitle_set.subtitle_items():
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


register(SRTGenerator)
