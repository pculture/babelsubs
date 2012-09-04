from babelsubs.generators.base import register, BaseGenerator


class DFXPGenerator(BaseGenerator):

    file_type = 'dfxp'

    def __init__(self, subtitle_set, line_delimiter=u'\n', language=None):
        super(DFXPGenerator, self).__init__(subtitle_set, line_delimiter,
                language)

    def __unicode__(self):
        return self.subtitle_set.to_xml()

    @classmethod
    def generate(cls, subtitle_set, language=None):
        return unicode(cls(subtitle_set=subtitle_set, language=language))


register(DFXPGenerator)
