from babelsubs.generators.base import BaseGenerator, register


class TXTGenerator(BaseGenerator):
    file_type = 'txt'

    def __unicode__(self):
        output = []
        for _, _, content in self.subtitle_set.subtitle_items(allow_format_tags=self.allows_formatting):
            content and output.append(content.strip())

        return self.line_delimiter.join(output)


register(TXTGenerator)
