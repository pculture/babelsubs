from datetime import timedelta
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
        time = timedelta(milliseconds=time)

        minutes, seconds = divmod(time.seconds, 60)
        hours, minutes = divmod(minutes, 60)

        return u'%01i:%02i:%02i.%03i' % (hours, minutes, seconds, time.microseconds / 1000)


register(SBVGenerator)
