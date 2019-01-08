from cgi import escape

from babelsubs.generators.base import BaseGenerator, register
from babelsubs.utils import UNSYNCED_TIME_FULL


class WEBVTTGenerator(BaseGenerator):
    file_type = 'vtt'

    def __init__(self, subtitle_set, language=None):
        super(WEBVTTGenerator, self).__init__(subtitle_set, language)
        self.line_delimiter = '\n'

    def __unicode__(self):
        output = ['WEBVTT\n']
        for subtitle in self.subtitle_set.subtitles:
            if subtitle.new_paragraph:
                output.append(u'NOTE Paragraph')
                output.append(u'')

            output.append(self.format_cue_header(subtitle))
            output.append(self.get_markup(subtitle.text))
            output.append(u'')
        return self.line_delimiter.join(output)[:-1]

    def get_markup(self, text):
        return text.replace("<br>", "\n")

    def format_cue_header(self, sub):
        parts = []
        parts.append(u'%s --> %s' % (
            self.format_time(sub.start_time),
            self.format_time(sub.end_time)
        ))
        if sub.region == 'top':
            parts.append('line:1')
        return ' '.join(parts)

    def format_time(self, milliseconds):
        if milliseconds is None:
            milliseconds = UNSYNCED_TIME_FULL

        seconds, milliseconds = divmod(int(milliseconds), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return u"%02i:%02i:%02i.%03i" % (hours, minutes, seconds, milliseconds)


register(WEBVTTGenerator)
