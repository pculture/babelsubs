import copy
from lxml import etree
from xml.sax.saxutils import escape as escape_xml
from babelsubs import utils
from babelsubs.generators.base import register, BaseGenerator
from babelsubs.storage import SubtitleSet
from babelsubs.xmlconst import *
from babelsubs.parsers.dfxp import milliseconds_to_time_clock_exp

BASE_TTML = '''\
<tt xml:lang="%(language_code)s" xmlns="%(namespace_uri)s" xmlns:tts="http://www.w3.org/ns/ttml#styling">
    <head>
        <metadata xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
            <ttm:title>%(title)s</ttm:title>
            <ttm:description>%(description)s</ttm:description>
            <ttm:copyright></ttm:copyright>
        </metadata>

        <styling xmlns:tts="http://www.w3.org/ns/ttml#styling">
            <style xml:id="amara-style"
                tts:color="white"
                tts:fontFamily="proportionalSansSerif"
                tts:fontSize="18px"
                tts:textAlign="center"
            />
        </styling>

        <layout xmlns:tts="http://www.w3.org/ns/ttml#styling">
            <region xml:id="amara-subtitle-area"
                    style="amara-style"
                    tts:extent="560px 62px"
                    tts:padding="5px 3px"
                    tts:backgroundColor="black"
                    tts:displayAlign="after"
            />
        </layout>
    </head>
    <body region="amara-subtitle-area">
        <div>
        </div>
    </body>
</tt>
'''

NAMESPACE_DECL = {
    'n': TTML_NAMESPACE_URI,
    'legacy':  TTML_NAMESPACE_URI_LEGACY,
    'styling': TTS_NAMESPACE_URI,
}
VALID_ROOT_ELS = ('tt', 'body', 'div')

def find_els(root_el, plain_xpath):
    """
    Since we might be using more than one namespace
    this simplifies searching for els that might be
    present in more than one namespace.
    You should send the plain_xpath string with no namespace
    declarations.
    Will return a list with 0 or more matching elements.
    """
    namespaces_names = NAMESPACE_DECL.keys()
    els = []
    for namespace_name in namespaces_names:
        if plain_xpath.startswith("/"):
            namespaced_xpath = "".join(['/%s:%s' % (namespace_name, el_name) for el_name in plain_xpath.split("/")[1:]])
        else:
            namespaced_xpath = "%s:%s" % (namespace_name, plain_xpath)
        els +=  root_el.xpath(namespaced_xpath, namespaces=NAMESPACE_DECL)
    return els


class DFXPGenerator(BaseGenerator):
    file_type = ['dfxp', 'xml', 'ttml']

    def __init__(self, subtitle_set, line_delimiter=u'\n', language=None):
        super(DFXPGenerator, self).__init__(subtitle_set, line_delimiter,
                language)

    def __unicode__(self):
        self._set_ttml(etree.fromstring(BASE_TTML % {
                'namespace_uri': TTML_NAMESPACE_URI,
                'title' : self.subtitle_set.title or '',
                'description': self.subtitle_set.description or '',
                'language_code': self.subtitle_set.language_code or '',
            }))
        for subtitle in self.subtitle_set.subtitles:
            self.append_subtitle(subtitle.start_time, subtitle.end_time, subtitle.text,
                                 new_paragraph=subtitle.new_paragraph,
                                 region=subtitle.region)
        return etree.tostring(self._ttml)

    def _find_divs(self):
        return find_els(self._body, "div")

    def _last_div(self):
        return self._find_divs()[-1]

    def _get_subtitles(self):
        result = []
        for div in self._find_divs():
            el_count = 0
            for el in find_els(div, 'p'):
                el_count += 1
                result.append(el)
        return result

    def append_subtitle(self, from_ms, to_ms, content, new_paragraph=False,
                        region=None, escape=True):
        """Append a subtitle to the end of the list.

        NO UNICODE ALLOWED!  USE XML ENTITIES TO REPRESENT UNICODE CHARACTERS!

        """

        if escape:
            content = escape_xml(content)
        content = self._fix_xml_content(content)
        p = self._create_subtitle_p(from_ms, to_ms, content)
        if region:
            p.set('region', region)

        if new_paragraph and len(self._last_div()) > 0:
            div = etree.SubElement(self._body, TTML + 'div')
        else:
            div = self._last_div()
        div.append(p)
        self._adjust_whitespace_after_append(div, p, new_paragraph)

    # couple of constants to easily create the text/tail attributes for the
    # elements we create inside the body
    _whitespace_before_p_tag = "\n" + " " * 12
    _whitespace_before_div_tag = "\n" + " " * 8
    _whitespace_after_last_div = "\n" + " " * 4

    def _adjust_whitespace_after_append(self, div, p, new_paragraph):
        if len(div) == 1:
            # first element added
            div.text = self._whitespace_before_p_tag
        else:
            div[-2].tail = self._whitespace_before_p_tag
        p.tail = self._whitespace_before_div_tag
        if new_paragraph:
            if len(self._body) > 1:
                self._body[-2].tail = self._whitespace_before_div_tag
            div.tail = self._whitespace_after_last_div

    def _create_subtitle_p(self, from_ms, to_ms, content):
        p = etree.fromstring(
            '<p xmlns="http://www.w3.org/ns/ttml">%s</p>' % content)

        if from_ms is not None:
            p.set('begin', milliseconds_to_time_clock_exp(from_ms))
        if to_ms is not None:
            p.set('end', milliseconds_to_time_clock_exp(to_ms))

        # fromstring has no sane way to set an attribute namespace (yay)
        # so we delete the old attrib, and add the new one with the prefixed
        # namespace
        spans = [el for el in p.getchildren() if el.tag.endswith('span')]
        for span in spans:
            for attr_name, value in span.attrib.items():
                if attr_name in ('fontStyle', 'textDecoration', 'fontWeight'):
                    span.set(TTS + attr_name, value)
                    del span.attrib[attr_name]
        return p

    _invalid_xml_control_chars_ascii = ''.join(chr(i) for i in xrange(32)
                                         if chr(i) not in "\n\r\t")
    _invalid_xml_control_chars_unicode = dict((i, None) for i in xrange(32)
                                              if chr(i) not in "\n\r\t")
    def _fix_xml_content(self, content):
        """Fix XML content.

        This method ensures the content doesn't include control chars that aren't valid in
            XML, should work for unicode or byte strings.
        """
        if isinstance(content, unicode):
            return content.translate(self._invalid_xml_control_chars_unicode)
        return content.translate(None, self._invalid_xml_control_chars_ascii)

    def _set_ttml(self, ttml):
        self._ttml = utils.indent_ttml(ttml)
        self._body = find_els(self._ttml, '/tt/body')[-1]

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
            ttml = etree.fromstring(BASE_TTML % {
                'namespace_uri': TTML_NAMESPACE_URI,
                'title' : '',
                'description': '',
                'language_code': '',
            })
            ttml = utils.indent_ttml(ttml)
            body = find_els(ttml, '/tt/body')[-1]
            body = ttml.find(TTML + 'body')
            body.remove(body.find(TTML + 'div'))
        else:
            ttml = initial_ttml
            body = ttml.find(TTML + 'body')
            if body is None:
                raise ValueError("no body tag")

        # set the default language to blank.  We will create a div for each
        # subtitle set and set xml:lang on that.
        ttml.set(XML + 'lang', '')

        # for each subtitle set we will append the body of tt
        for i, subtitle_set in enumerate(subtitle_sets):
            root_elt = copy.deepcopy(ttml)
            language_code = root_elt.get(XML + 'lang')
            lang_div = etree.SubElement(body, TTML + 'div')
            lang_div.set(XML + 'lang', language_code)
            lang_div.extend(root_elt.find(TTML + 'body').findall(TTML + 'div'))
        ttml = utils.indent_ttml(ttml)
        return etree.tostring(ttml)


register(DFXPGenerator)
