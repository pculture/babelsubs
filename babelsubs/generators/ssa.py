import codecs
from babelsubs import utils
from babelsubs.generators.base import BaseGenerator, register

class SSAGenerator(BaseGenerator):
    file_type = ['ssa', 'ass']

    MAPPINGS = dict(bold="{\\b1}%s{\\b0}",
                    italics="{\i1}%s{\i0}", underline="{\u1}%s{\u0}")


    def __unicode__(self):
        #add BOM to fix python default behaviour, because players don't play without it
        return u''.join([unicode(codecs.BOM_UTF8, "utf8"), self._start(), self._content(), self._end()])

    def _start(self):
        ld = self.line_delimiter
        return u'[Script Info]%sTitle: %s%s' % (ld, getattr(self, 'title', ''), ld)

    def _end(self):
        return u''

    def format_time(self, milliseconds):
        if milliseconds is None:
            components = utils.unsynced_time_components(one_hour_digit=True, uses_centiseconds=True)
        else:
            components = utils.milliseconds_to_time_clock_components(
            milliseconds,
            unsynced_val=utils.UNSYNCED_TIME_ONE_HOUR_DIGIT,
            use_centiseconds=True)
        return u'%(hours)i:%(minutes)02i:%(seconds)02i.%(centiseconds)02i' % components

    def _clean_text(self, text):
        return text.replace('\n', ' ')

    def _content(self):
        dl = self.line_delimiter
        output = []
        output.append(u'[Events]%s' % dl)
        output.append(u'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text%s' % dl)
        tpl = u'Dialogue: 0,%s,%s,Default,,0000,0000,0000,,%s%s'

        for from_ms, to_ms, content, meta in self.subtitle_set.subtitle_items(self.MAPPINGS):
            start = self.format_time(from_ms)
            end = self.format_time(to_ms)
            text = self._clean_text(content)
            output.append(tpl % (start, end, text, dl))

        return ''.join(output)

register(SSAGenerator)
