from babelsubs.generators.base import BaseGenerator, register

def format_srt_time(milliseconds):
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%02i:%02i:%02i,%03i" % (hours, minutes, seconds, milliseconds)

class SRTGenerator(BaseGenerator):
    file_type = 'srt'

    def __init__(self, subtitle_set):
        self.line_delimiter = '\r\n'
        self.subtitle_set = subtitle_set
        super(SRTGenerator, self).__init__(subtitle_set)

    def __unicode__(self):
        output = []
        i = 1
        # FIXME: allow formatting tags
        for from_ms, to_ms, content in self.subtitle_set.subtitle_items(allow_format_tags=False):
            output.append(unicode(i))
            output.append(u'%s --> %s' % (
                format_srt_time(from_ms),
                format_srt_time(to_ms)
            ))
            output.append(content)
            output.append(u'')
            i += 1
        return self.line_delimiter.join(output)


register(SRTGenerator)
