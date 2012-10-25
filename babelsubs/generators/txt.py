from babelsubs.generators.base import BaseGenerator, register


class TXTGenerator(BaseGenerator):
    file_type = 'txt'

    def __unicode__(self):
        output = []
        for _, _, content, _ in self.subtitle_set.subtitle_items():
            content and output.append(content.strip())

        return self.line_delimiter.join(output)


register(TXTGenerator)
