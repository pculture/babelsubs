from cgi import escape
from babelsubs.generators.base import BaseGenerator, register
from babelsubs.utils import UNSYNCED_TIME_FULL


class SRTGenerator(BaseGenerator):
    file_type = 'srt'

    def __init__(self, subtitle_set, language=None):
        super(SRTGenerator, self).__init__(subtitle_set, language)
        self.line_delimiter = '\r\n'

    def __unicode__(self):
        output = []
        i = 1
        for subtitle in self.subtitle_set.subtitles:
            output.append(unicode(i))
            output.append(u'%s --> %s' % (
                self.format_time(subtitle.start_time),
                self.format_time(subtitle.end_time)
            ))
            text = self.get_markup(subtitle.text)
            output.append(text)
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

    def get_markup(self, text):
        return text.replace("<br>", "\n")

register(SRTGenerator)
