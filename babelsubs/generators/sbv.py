from math import floor
from babelsubs.generators.base import BaseGenerator, register


class SBVGenerator(BaseGenerator):
    file_type = 'sbv'

    def __init__(self, subtitles_set, line_delimiter=u'\r\n', language=None):
        super(SBVGenerator, self).__init__(subtitles_set, line_delimiter,
                language)

    def __unicode__(self):
        output = []

        for from_ms, to_ms, content in self.subtitle_set.subtitle_items(allow_format_tags=self.allows_formatting):
            if self.isnumber(from_ms) and self.isnumber(to_ms):
                start = self.format_time(from_ms)
                end = self.format_time(to_ms)
                output.append(u'%s,%s' % (start, end))
                output.append(content.strip())
                output.append(u'')

        return self.line_delimiter.join(output)

    def format_time(self, time):
        time = float(time) / 1000.0
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 9
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 1000)
        return u'%01i:%02i:%02i.%03i' % (hours, minutes, seconds, fr_seconds)


register(SBVGenerator)
