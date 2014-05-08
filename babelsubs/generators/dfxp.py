from lxml import etree
from babelsubs.generators.base import register, BaseGenerator
from babelsubs.storage import SubtitleSet

class DFXPGenerator(BaseGenerator):
    """
    Since the internal storage is already in dfxp, the generator is just
    a small shim to keep the public interface between all generators
    regular.
    """
    file_type = ['dfxp', 'xml' ]

    def __init__(self, subtitle_set, line_delimiter=u'\n', language=None):
        super(DFXPGenerator, self).__init__(subtitle_set, line_delimiter,
                language)

    def __unicode__(self):
        return self.subtitle_set.to_xml()

    @classmethod
    def generate(cls, subtitle_set, language=None):
        return unicode(cls(subtitle_set=subtitle_set, language=language))

    @classmethod
    def merge_subtitles(cls, subtitle_sets):
        """Combine multiple subtitles sets into a single XML string.
        """
        if len(subtitle_sets) == 0:
            raise TypeError("DFXPGenerator.merge_subtitles: No subtitles given")
        # define some namespaced attribute names for ease of use
        lang = '{http://www.w3.org/XML/1998/namespace}lang'
        body = '{http://www.w3.org/ns/ttml}body'
        div = '{http://www.w3.org/ns/ttml}div'

        # create XML for empty subtitles, with xml:lang=""
        result = SubtitleSet('').as_etree_node()
        result_body = result.find(body)
        result_body.remove(result_body.find(div))

        # for each subtitle set we will append the body of result
        for i, subtitle_set in enumerate(subtitle_sets):
            root_elt = subtitle_set.as_etree_node()
            language_code = root_elt.get(lang)
            content_div = root_elt.find(body).find(div)
            content_div.set(lang, language_code)
            result_body.append(content_div)
            # for every subtitle set except the last, we add some extra
            # whitespace to make things look pretty
            if i < len(subtitle_sets) - 1:
                if content_div.tail is not None:
                    content_div.tail += '    '
        return etree.tostring(result)

register(DFXPGenerator)
