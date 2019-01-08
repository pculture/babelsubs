from babelsubs.generators.base import BaseGenerator, register
from babelsubs.utils import UNSYNCED_TIME_ONE_HOUR_DIGIT

class SBVGenerator(BaseGenerator):
    file_type = 'sbv'

    def __init__(self, subtitles_set, line_delimiter=u'\r\n', language=None):
        super(SBVGenerator, self).__init__(subtitles_set, line_delimiter,
                language)

    def __unicode__(self):
        output = []
        for subtitle in self.subtitle_set.subtitles:
            start = self.format_time(subtitle.start_time)
            end = self.format_time(subtitle.end_time)
            output.append(u'{},{}'.format(start, end))
            text = self.get_markup(subtitle.text)
            output.append(text.strip())
            output.append(u'')

        return self.line_delimiter.join(output)

    def format_time(self, time):
        if time is None:
            time = UNSYNCED_TIME_ONE_HOUR_DIGIT
        seconds, milliseconds = divmod(int(time), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        return u'%01i:%02i:%02i.%03i' % (hours, minutes, seconds, milliseconds)

    def get_markup(self, text):
        return text.replace("<br>", "[br]")

register(SBVGenerator)
