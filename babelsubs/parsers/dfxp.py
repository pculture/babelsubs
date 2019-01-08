import os
import re

from babelsubs.storage import SubtitleSet
from babelsubs import utils
from babelsubs.xmlconst import *
from base import BaseTextParser, SubtitleParserError, register
from xml.parsers.expat import ExpatError
from xml.sax.saxutils import escape as escape_xml
from lxml import etree
from lxml.etree import XMLSyntaxError

MAX_SUB_TIME = (60 * 60 * 100) - 1

# TODO: Use defusedxml to parse TTML/DFXP/XML

SCHEMA_PATH =  os.path.join(os.getcwd(), "data", 'xsdchema', 'all.xsd')
#schema = lxml.etree.XMLSchema(lxml.etree.parse(open(SCHEMA_PATH)))

TIME_EXPRESSION_METRIC = re.compile(r'(?P<num>[\d]+(\.\d+)?)(?P<unit>(h|ms|s|m|f|t))')
TIME_EXPRESSION_CLOCK_TIME = re.compile(r'(?P<hours>[\d]{2,3}):(?P<minutes>[\d]{2}):(?P<seconds>[\d]{2})(?:.(?P<fraction>[\d]{1,3}))?')

NEW_PARAGRAPH_META_KEY = 'new_paragraph'
REGION_META_KEY = 'region'
TTML_NAMESPACE_URI_LEGACY_RE =           re.compile(r'''('|")(%s)(#[\w]+)("|')''' % TTML_NAMESPACE_URI_LEGACY)
TTML_NAMESPACE_URI_LEGACY_NO_ANCHOR_RE = re.compile(r'''('|")(%s)("|')''' % TTML_NAMESPACE_URI_LEGACY)

MULTIPLE_SPACES_RE = re.compile(r"\s{2,}")
NEW_LINES_RE = re.compile(r'(\n|\r)')


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

def get_attr(el, attr):
    """Get the string of an attribute, or None if it's not present.

    Ignores namespaces to save your sanity.

    """
    for k, v in el.attrib.items():
        if k == attr or k.rsplit('}', 1)[-1] == attr:
            return v

def element_tag(el):
    """Get the tag name for an element.

    This works around a ETree bug where for most elements, el.tag is a string,
    but for comment nodes it's a method.
    """
    if not hasattr(el.tag, '__call__'):
        return el.tag
    else:
        return el.tag()

def get_contents(el):
    """Get the contents of the given element as a string of XML.
    """
    return "".join([x for x in el.itertext()]).strip()

def _cleanup_legacy_namespace(input_string):
    """
    At some point in time, the ttml namespace was TTML_NAMESPACE_URI_LEGACY,
    then it got changed to TTML_NAMESPACE_URI. There are tons of those floating
    around, including our pre-dmr dfxps and ttmls files. The backend (this lib)
    can deal with both namespaces, but the amara front end cannot. We therefore
    convert all namespaces to the correct one (else a lot of namespace xml magic
    has to be done on the front end, and trust me, you don't want to do it).

    This function 'converts' all ...ttfa... to ...ttml... with a regex. To be a
    bit less reckless, we're checking that it's quoted, as in an attribute. (that
    of course doesn't guarantee the safety of this, just makes it a bit less
    likely that the legacy url is being used inside a text node. All of this
    because lxml cannot change namespace attribute values:
     https://bugs.launchpad.net/lxml/+bug/555602
    """
    input_string =  TTML_NAMESPACE_URI_LEGACY_NO_ANCHOR_RE.sub(r'"%s\3' % TTML_NAMESPACE_URI, input_string)
    return TTML_NAMESPACE_URI_LEGACY_RE.sub(r'"%s\3\4' % TTML_NAMESPACE_URI, input_string)


def to_clock_time(time_expression, tick_rate=None):
    """
    If time expression is not in clock time, transform it
    """
    match = TIME_EXPRESSION_CLOCK_TIME.match(time_expression)
    if match:
        return time_expression
    return milliseconds_to_time_clock_exp(time_expression_to_milliseconds(time_expression, tick_rate))

def milliseconds_to_time_clock_exp(milliseconds):
    """
    Converts time components to a string suitable to be used on time expression
    fot ttml
    """
    if milliseconds is None:
        return None
    expression = '%(hours)02d:%(minutes)02d:%(seconds)02d.%(milliseconds)03d'
    return expression % utils.milliseconds_to_time_clock_components(milliseconds)

def time_expression_to_milliseconds(time_expression, tick_rate=None):
    """
    Parses possible values from time expressions[1] to a normalized value
    in milliseconds.

    We don't support all possible forms now, only clock time, metric and tick.
    [1] http://www.w3.org/TR/ttaf1-dfxp/#timing-value-timeExpression
    """
    if not time_expression:
        return 0
    match = TIME_EXPRESSION_CLOCK_TIME.match(time_expression)
    if match:
        groups = match.groupdict()
        hour = int(groups['hours'])
        minutes = int(groups['minutes'])
        seconds  = int(groups['seconds'])
        milliseconds = int(groups['fraction'] or 0)
        return (((hour * 3600) + (minutes * 60) + seconds ) * 1000 ) + milliseconds
    match = TIME_EXPRESSION_METRIC.match(time_expression)
    if match:
        groups = match.groupdict()
        num, unit = float(groups['num']), groups['unit']
        if unit == 't':
            if not tick_rate:
                raise ValueError("Ticks need a tick rate, mate.")
            return 1000 * (num / float(tick_rate))
        multiplier = {
            "h": 3600 * 1000,
            "m": 60 * 1000,
            "s": 1000,
            "ms": 1,
            'f': 0,
        }.get(unit, None)
        return num * multiplier
    # Time expression can't be parsed
    return None


class DFXPParser(BaseTextParser):
    file_type = ['dfxp', 'xml', 'ttml']
    NO_UNICODE = True

    def __init__(self, input_string, language=None):
        # convert legacy ttfa namespace to the final one
        input_string = _cleanup_legacy_namespace(input_string)
        # we remove *all* extraneous whitespace, since we pretty print
        # the xml and we introduce space back. Right now, we're taking
        # the easy way out and ignoring xml:spaces='preserve'
        input_string = NEW_LINES_RE.sub("", input_string)
        input_string = MULTIPLE_SPACES_RE.sub(" ", input_string)

        try:
            self._set_ttml(etree.fromstring(input_string,
                           parser=etree.XMLParser(remove_blank_text=True)))
            # now, if there's a space after a <br> tag, we don't want it here.
            # most likely it was created by indenting. But *only* it it's after a
            # <br> tag, so we must loop through them
            for node in find_els(self._ttml, "/tt/body/div/*/br"):
                node.tail = node.tail.lstrip() if node.tail else None
            self.tick_rate = self._get_tick_rate()

            [self.normalize_time(x) for x in self.get_subtitles()]
            subtitles = self.subtitle_items()
            self.subtitle_set = SubtitleSet.from_list(language, subtitles)
        except (XMLSyntaxError, ExpatError) as e:
            raise SubtitleParserError("There was an error while we were parsing your xml", e)


    def __len__(self):
        return self.subtitle_set.__len__()

    def __nonzero__(self):
        return self.subtitle_set.__nonzero__()

    def _set_ttml(self, ttml):
        self._ttml = utils.indent_ttml(ttml)
        self._body = find_els(self._ttml, '/tt/body')[-1]

    def to_internal(self):
        return self.subtitle_set

    def normalize_time(self, el):
        """
        Transforms begin,dur pairs into begin,end pairs
        also uses clock time expressions (00:00:00).

        Changes node in place
        """
        begin = get_attr(el, 'begin')
        if begin:
            begin = to_clock_time(begin, self.tick_rate)
        end = get_attr(el, 'end')
        if end:
            end = to_clock_time(end, self.tick_rate)
        dur = get_attr(el, 'dur')
        if dur:
            end= milliseconds_to_time_clock_exp(
                time_expression_to_milliseconds(begin, self.tick_rate) + \
                time_expression_to_milliseconds(dur, self.tick_rate))
            el.attrib.pop('dur')
        if begin:
            el.attrib['begin'] = begin
        if end:
            el.attrib['end'] = end

    def subtitle_items(self):
        """
        Return a list of (from_ms, to_ms, content, meta) tuples.

        The from and to millisecond values may be any time expression
        that we can parse.

        Meta is a dict with additional information.
        """
        result = []

        for el in self.get_subtitles():
            # bool(el.getprevious()) doesn't do what you'd think
            # use 'is None'
            meta = {
                'new_paragraph': (el.getprevious() is None),
                'region': get_attr(el, 'region'),
            }
            result.append(self._extract_from_el(el, meta))

        return result

    def get_subtitles(self):
        result = []

        for div in self.find_divs():
            el_count = 0

            for el in find_els(div, 'p'):
                el_count += 1
                result.append(el)

        return result

    def find_divs(self):
        return find_els(self._body, "div")

    def last_div(self):
        return self.find_divs()[-1]

    def _get_tick_rate(self):
        try:
            tt = self.find_divs()[0]
        except IndexError as e:
            raise SubtitleParserError(
                "No valid root elements found, we'll accept 'tt, body and div",
                original_error=e)
        for name,value in tt.attrib.items():
            if name == "tickRate":
                return int(value)
        return 1

    def _extract_from_el(self, el, meta):
        begin = get_attr(el, 'begin')
        end = get_attr(el, 'end')


        from_ms = (time_expression_to_milliseconds(begin)
                if begin  is not None and begin is not '' else None)
        to_ms = (time_expression_to_milliseconds(end)
                if end is not None and end is not '' else None)
        content = self.get_markup(el)

        return (from_ms, to_ms, content, meta)

    def get_markup(self, el):
        return self._get_content_with_markup(el).strip()

    def _get_content_with_markup(self, el):
        text = []
        if el.text:
            text.append(el.text)
        for child in el:
            tag = self.__clear_namespace(element_tag(child))

            if tag == 'span':
                template = self._template_for_span(child)
                text.append(template %
                            (self._get_content_with_markup(child),))

            elif tag == "br":
                    text.append("<br>")

            if child.tail:
                text.append(child.tail)

        return ''.join(text)

    def _template_for_span(self, elt):
        """String to use for a span for get_markup().

        The returned string will contain a single "%s" value to be filled in
        with the contents of the span.
        """
        # no i don't want to deal with namespaces right now sorry
        attrs = dict([(self.__clear_namespace(n), v)
                      for n, v in elt.items()])

        template = "{}"
        if attrs.get('fontWeight', '') == 'bold':
            template = template.format("<b>%s</b>")

        if attrs.get('fontStyle', '') == 'italic':
            template = template.format("<i>%s</i>")

        if attrs.get('textDecoration', '') == 'underline':
            template = template.format("<u>%s</u>")
        return template

    def __clear_namespace(self, name):
        return name.split("}")[-1] if '}' in name else name

register(DFXPParser)
