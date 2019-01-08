import codecs
from babelsubs import utils
from babelsubs.generators.base import BaseGenerator, register

class SSAGenerator(BaseGenerator):
    file_type = ['ssa', 'ass']

    def __unicode__(self):
        # add BOM to fix python default behaviour, because players don't play without it
        return u''.join([unicode(codecs.BOM_UTF8, "utf8"),
                        self._start(), self._content(), self._end()])

    def _start(self):
        return u'[Script Info]{}Title: {}{}'.format(self.line_delimiter,
                                                    getattr(self, 'title', ''),
                                                    self.line_delimiter)

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

    def _content(self):
        output = []
        output.append(u'[Events]' + self.line_delimiter)
        output.append(u'Format: Layer, Start, End, Style, Name, MarginL, MarginR, ' +
                      u'MarginV, Effect, Text' + self.line_delimiter)
        template = u'Dialogue: 0,{},{},Default,,0000,0000,0000,,{}{}'

        for subtitle in self.subtitle_set.subtitles:
            start = self.format_time(subtitle.start_time)
            end = self.format_time(subtitle.end_time)
            text = self.get_markup(subtitle.text)
            output.append(template.format(start, end, text, self.line_delimiter))

        return ''.join(output)

    def get_markup(self, text):
        text = text.replace("<b>", "{\\b1}").replace("</b>", "{\\b0}")
        text = text.replace("<i>", "{\\i1}").replace("</i>", "{\\i0}")
        text = text.replace("<u>", "{\\u1}").replace("</u>", "{\\u0}")
        text = text.replace("<br>", "\N")
        return text.replace("\n", "")

register(SSAGenerator)
