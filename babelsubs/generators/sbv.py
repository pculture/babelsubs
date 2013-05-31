from babelsubs.generators.base import BaseGenerator, register
from babelsubs.utils import UNSYNCED_TIME_ONE_HOUR_DIGIT

class SBVGenerator(BaseGenerator):
    file_type = 'sbv'

    MAPPINGS = dict(linebreaks="[br]")

    def __init__(self, subtitles_set, line_delimiter=u'\r\n', language=None):
        super(SBVGenerator, self).__init__(subtitles_set, line_delimiter,
                language)

    def __unicode__(self):
        output = []

        for from_ms, to_ms, content, meta in self.subtitle_set.subtitle_items(self.MAPPINGS):
            start = self.format_time(from_ms)
            end = self.format_time(to_ms)
            output.append(u'%s,%s' % (start, end))
            output.append(content.strip())
            output.append(u'')

        return self.line_delimiter.join(output)

    def format_time(self, time):
        if time is None:
            time = UNSYNCED_TIME_ONE_HOUR_DIGIT
        seconds, milliseconds = divmod(int(time), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        return u'%01i:%02i:%02i.%03i' % (hours, minutes, seconds, milliseconds)


register(SBVGenerator)
