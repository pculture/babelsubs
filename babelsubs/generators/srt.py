from babelsubs.generators.base import BaseGenerator, register


class SRTGenerator(BaseGenerator):
    file_type = 'srt'

    MAPPINGS = dict(linebreaks="\n", bold="<b>%s</b>",
                    italics="<i>%s</i>", underline="<u>%s</u>")

    def __init__(self, subtitle_set, language=None):
        super(SRTGenerator, self).__init__(subtitle_set, language)
        self.line_delimiter = '\r\n'

    def __unicode__(self):
        output = []
        i = 1
        # FIX ME: allow formatting tags
        for from_ms, to_ms, content, meta in self.subtitle_set.subtitle_items(mappings=self.MAPPINGS):
            output.append(unicode(i))
            output.append(u'%s --> %s' % (
                self._format_srt_time(from_ms),
                self._format_srt_time(to_ms)
            ))
            output.append(content)
            output.append(u'')
            i += 1
        return self.line_delimiter.join(output)

    def _format_srt_time(self, milliseconds):
        seconds, milliseconds = divmod(int(milliseconds), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%02i:%02i:%02i,%03i" % (hours, minutes, seconds, milliseconds)


register(SRTGenerator)
