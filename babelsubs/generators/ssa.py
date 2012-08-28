import codecs

from math import floor
from babelsubs.generators.base import BaseGenerator, register

class SSAGenerator(BaseGenerator):
    file_type = 'ssa'

    def __unicode__(self):
        #add BOM to fix python default behaviour, because players don't play without it
        return u''.join([unicode(codecs.BOM_UTF8, "utf8"), self._start(), self._content(), self._end()])

    def _start(self):
        ld = self.line_delimiter
        return u'[Script Info]%sTitle: %s%s' % (ld, getattr(self, 'title', ''), ld)

    def _end(self):
        return u''

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 9
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%i:%02i:%02i.%02i' % (hours, minutes, seconds, fr_seconds)

    def _clean_text(self, text):
        return text.replace('\n', ' ')

    def _content(self):
        dl = self.line_delimiter
        output = []
        output.append(u'[Events]%s' % dl)
        output.append(u'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text%s' % dl)
        tpl = u'Dialogue: 0,%s,%s,Default,,0000,0000,0000,,%s%s'
        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                text = self._clean_text(item['text'].strip())
                output.append(tpl % (start, end, text, dl))
        return ''.join(output)

register(SSAGenerator)
