from lxml import etree
from babelsubs import utils
from babelsubs.generators.base import register, BaseGenerator
from babelsubs.storage import SubtitleSet
from babelsubs.xmlconst import *

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
    def merge_subtitles(cls, subtitle_sets, initial_ttml=None):
        """Combine multiple subtitles sets into a single XML string.
        """
        if len(subtitle_sets) == 0:
            raise TypeError("DFXPGenerator.merge_subtitles: No subtitles given")

        if initial_ttml is None:
            tt = SubtitleSet('').as_etree_node()
            body = tt.find(TTML + 'body')
            body.remove(body.find(TTML + 'div'))
        else:
            tt = initial_ttml
            body = tt.find(TTML + 'body')
            if body is None:
                raise ValueError("no body tag")

        # set the default language to blank.  We will create a div for each
        # subtitle set and set xml:lang on that.
        tt.set(XML + 'lang', '')

        # for each subtitle set we will append the body of tt
        for i, subtitle_set in enumerate(subtitle_sets):
            root_elt = subtitle_set.as_etree_node()
            language_code = root_elt.get(XML + 'lang')
            lang_div = etree.SubElement(body, TTML + 'div')
            lang_div.set(XML + 'lang', language_code)
            lang_div.extend(root_elt.find(TTML + 'body').findall(TTML + 'div'))
        utils.indent_ttml(tt)
        return etree.tostring(tt)

register(DFXPGenerator)
