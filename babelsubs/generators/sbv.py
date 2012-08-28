from math import floor

from babelsubs.generators.base import BaseGenerator, register

class SBVGenerator(BaseGenerator):
    file_type = 'sbv'

    def __init__(self, subtitles,  line_delimiter=u'\r\n', language=None):
        super(SBVGenerator, self).__init__(subtitles, line_delimiter)

    def __unicode__(self):
        output = []

        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                output.append(u'%s,%s' % (start, end))
                output.append(item['text'].strip())
                output.append(u'')

        return self.line_delimiter.join(output)

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 9
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 1000)
        return u'%01i:%02i:%02i.%03i' % (hours, minutes, seconds, fr_seconds)

register(SBVGenerator)
