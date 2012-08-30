from babelsubs.generators.base import BaseGenerator, register


class SRTGenerator(BaseGenerator):
    file_type = 'srt'

    def __init__(self, subtitle_set, language=None):
        super(SRTGenerator, self).__init__(subtitle_set, language)
        self.line_delimiter = '\r\n'

    def __unicode__(self):
        output = []
        i = 1
        # FIXME: allow formatting tags
        for from_ms, to_ms, content in self.subtitle_set.subtitle_items(allow_format_tags=self.allows_formatting):
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
