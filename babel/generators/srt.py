from math import floor
from HTMLParser import HTMLParser

from babel.generators.base import BaseGenerator, register

class SRTGenerator(BaseGenerator):
    file_type = 'srt'

    def __init__(self, subtitles, line_delimiter=u'\r\n', language=None):
        super(SRTGenerator, self).__init__(subtitles, line_delimiter)

    def __unicode__(self):
        output = []

        parser = HTMLParser()
        i = 1
        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                output.append(unicode(i))
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                output.append(u'%s --> %s' % (start, end))
                output.append(parser.unescape(item['text']).strip())
                output.append(u'')
                i += 1

        return self.line_delimiter.join(output)

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 99
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%02i:%02i:%02i,%03i' % (hours, minutes, seconds, fr_seconds)

register(SRTGenerator)
