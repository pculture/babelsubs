from babelsubs.generators.base import register, BaseGenerator


class DFXPGenerator(BaseGenerator):
    """
    Since the internal storage is already in dfxp, the generator is just
    a small shim to keep the public interface between all generators
    regular.
    """
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
