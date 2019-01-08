from babelsubs.generators.base import BaseGenerator, register


class TXTGenerator(BaseGenerator):
    file_type = 'txt'

    def __init__(self, subtitle_set, line_delimiter=u'\n\n', language=None):
        """
        Generator is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds'}
        """
        self.subtitle_set = subtitle_set
        self.line_delimiter = line_delimiter
        self.language = language

    def __unicode__(self):
        output = []
        for subtitle in self.subtitle_set.subtitles:
            if subtitle.text:
                output.append(subtitle.text.replace("<br>", "\n").strip())
        return self.line_delimiter.join(output)


register(TXTGenerator)
