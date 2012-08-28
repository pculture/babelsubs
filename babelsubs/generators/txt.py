from babelsubs.generators.base import BaseGenerator, register

class TXTGenerator(BaseGenerator):
    file_type = 'txt'

    def __init__(self, subtitles, line_delimiter=u'\r\n\r\n', language=None):
        super(TXTGenerator, self).__init__(subtitles, line_delimiter)

    def __unicode__(self):
        output = []
        for item in self.subtitles:
            item['text'] and output.append(item['text'].strip())

        return self.line_delimiter.join(output)

register(TXTGenerator)
