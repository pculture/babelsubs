# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

import copy
import difflib
from itertools import izip_longest, izip
import os
import re
from lxml import etree
from xml.sax.saxutils import (escape as escape_xml,
                              unescape as unescape_xml)
from collections import namedtuple

from babelsubs import utils
from babelsubs.xmlconst import *

SCHEMA_PATH =  os.path.join(os.getcwd(), "data", 'xsdchema', 'all.xsd')
#schema = lxml.etree.XMLSchema(lxml.etree.parse(open(SCHEMA_PATH)))

TIME_EXPRESSION_METRIC = re.compile(r'(?P<num>[\d]+(\.\d+)?)(?P<unit>(h|ms|s|m|f|t))')
TIME_EXPRESSION_CLOCK_TIME = re.compile(r'(?P<hours>[\d]{2,3}):(?P<minutes>[\d]{2}):(?P<seconds>[\d]{2})(?:.(?P<fraction>[\d]{1,3}))?')

NEW_PARAGRAPH_META_KEY = 'new_paragraph'
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

SubtitleLine = namedtuple("SubtitleLine", ['start_time', 'end_time', 'text', 'meta'])

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
    raise ValueError("Time expression %s can't be parsed" % time_expression)


def milliseconds_to_time_clock_exp(milliseconds):
    """
    Converts time components to a string suitable to be used on time expression
    fot ttml
    """
    if milliseconds is None:
        return None
    expression = '%(hours)02d:%(minutes)02d:%(seconds)02d.%(milliseconds)03d'
    return expression % utils.milliseconds_to_time_clock_components(milliseconds)

def to_clock_time(time_expression, tick_rate=None):
    """
    If time expression is not in clock time, transform it
    """
    match = TIME_EXPRESSION_CLOCK_TIME.match(time_expression)
    if match:
        return time_expression
    return milliseconds_to_time_clock_exp(time_expression_to_milliseconds(time_expression, tick_rate))

class _Differ(object):
    """Class that does the work for diff()."""
    def __init__(self, set_1, set_2, mappings):
        self.items1 = set_1.subtitle_items(mappings)
        self.items2 = set_2.subtitle_items(mappings)

    def _subs_sequence(self, items):
        return [(i.start_time, i.end_time, i.text) for i in items]

    def _time_sequence(self, items):
        return [(s.start_time, s.end_time) for s in items]

    def _text_sequence(self, items):
        return [(s.text,) for s in items]

    def calc_diff(self):
        return {
            'text_changed': self.calc_text_changed(),
            'time_changed': self.calc_time_changed(),
            'changed': self.items1 != self.items2,
            'subtitle_data': self.calc_subtitle_data(),
        }

    def calc_time_changed(self):
        sm = difflib.SequenceMatcher(None, self._time_sequence(self.items1),
                                     self._time_sequence(self.items2))
        return 1.0 - sm.ratio()

    def calc_text_changed(self):
        sm = difflib.SequenceMatcher(None, self._text_sequence(self.items1),
                                     self._text_sequence(self.items2))
        return 1.0 - sm.ratio()

    def calc_subtitle_data(self):
        # when calculating the diff, we only match against the times/text and
        # ignore the meta.
        sm = difflib.SequenceMatcher(None,
                                     self._subs_sequence(self.items1),
                                     self._subs_sequence(self.items2))
        rv = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for i, j in izip(xrange(i1, i2), xrange(j1, j2)):
                    rv.append(self.make_subtitle_data_item(i, j))
            elif tag == 'replace':
                for i, j in izip_longest(xrange(i1, i2), xrange(j1, j2)):
                    if i is None:
                        rv.append(self.make_subtitle_data_item(None, j))
                    elif j is None:
                        rv.append(self.make_subtitle_data_item(i, None))
                    else:
                        rv.append(self.make_subtitle_data_item(i, j))

            elif tag == 'delete':
                for i in xrange(i1, i2):
                    rv.append(self.make_subtitle_data_item(i, None))
            elif tag == 'insert':
                for j in xrange(j1, j2):
                    rv.append(self.make_subtitle_data_item(None, j))
        return rv

    def make_subtitle_data_item(self, i, j):
        if i is not None:
            s1 = self.items1[i]
        else:
            s1 = SubtitleLine(None, None, None, None)
        if j is not None:
            s2 = self.items2[j]
        else:
            s2 = SubtitleLine(None, None, None, None)
        return {
            'time_changed': ((s1.start_time, s1.end_time) !=
                             (s2.start_time, s2.end_time)),
            'text_changed': s1.text != s2.text,
            'subtitles': (s1, s2),
        }

def diff(set_1, set_2, mappings=None):
    """
    Performs a simple diff, only taking into account:
    - Start and end time
    - Text

    The returned data structure looks like this:
    {
        changed : bool (true if either text_changed or time_changed > 0)
        text_changed: (float between 0 and 1)
        time_changed: (float between 0 and 1)
        subtitle_data: [
            {
                time_changed: bool,
                text_changed: bool,
                subtitles: [subtitle_line1, subtitle_line2],
            }, ... ordered list with both subtitles. If one list is longer , you
            will get an empty SubtitleLine named tupple
        ]
    """
    return _Differ(set_1, set_2, mappings).calc_diff()

def calc_changes(set_1, set_2, mappings=None):
    """Returns time/text changes for two subtitle sets.

    :returns: (text_changed, time_changed) tuple
    """
    differ = _Differ(set_1, set_2, mappings)
    return differ.calc_text_changed(), differ.calc_time_changed()

class SubtitleSet(object):
    BASE_TTML = '''\
<tt xml:lang="%(language_code)s" xmlns="%(namespace_uri)s" xmlns:tts="http://www.w3.org/ns/ttml#styling" >
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

    def __init__(self, language_code, initial_data=None, title=None,
                 description=None, normalize_time=True):
        """Create a new set of Subtitles, either empty or from a hunk of TTML.

        language_code: The bcp47 code for this language.
        initial_data: any optional xml as the starting point.
        NO UNICODE ALLOWED!  USE XML ENTITIES TO REPRESENT UNICODE CHARACTERS!

        """
        if initial_data:
            # convert legacy ttfa namespace to the final one
            initial_data = _cleanup_legacy_namespace(initial_data)
            # we remove *all* extraneous whitespace, since we pretty print
            # the xml and we introduce space back. Right now, we're taking
            # the easy way out and ignoring xml:spaces='preserve'
            initial_data = NEW_LINES_RE.sub("", initial_data)
            initial_data = MULTIPLE_SPACES_RE.sub(" ", initial_data)

            self._set_ttml(etree.fromstring(initial_data,
                parser=etree.XMLParser(remove_blank_text=True)))
            # now, if there's a space after a <br> tag, we don't want it here.
            # most likely it was created by indenting. But *only* it it's after a
            # <br> tag, so we must loop through them
            for node in find_els(self._ttml, "/tt/body/div/*/br"):
                node.tail = node.tail.lstrip() if node.tail else None
            self.tick_rate = self._get_tick_rate()
            if normalize_time:
                [self.normalize_time(x) for x in self.get_subtitles()]
        else:
            self._set_ttml(etree.fromstring(SubtitleSet.BASE_TTML % {
                'namespace_uri': TTML_NAMESPACE_URI,
                'title' : title or '',
                'description': description or '',
                'language_code': language_code or '',
            }))

        if initial_data:
            self.subtitles = self.subtitle_items()
        else:
            self.subtitles = None

    @classmethod
    def create_with_raw_ttml(cls, ttml):
        self = cls.__new__(cls)
        self._set_ttml(ttml)
        # force subtitles to be created
        self.subtitle_items()
        return self

    def _set_ttml(self, ttml):
        utils.indent_ttml(ttml)
        self._ttml = ttml
        self._body = find_els(self._ttml, '/tt/body')[-1]

    def __len__(self):
        return len(self.get_subtitles())

    def __getitem__(self, key):
        if self.subtitles is None:
            self.subtitles = self.subtitle_items()
        return self.subtitles[key]

    def find_divs(self):
        return find_els(self._body, "div")

    def last_div(self):
        return self.find_divs()[-1]

    def get_subtitles(self):
        result = []

        for div in self.find_divs():
            el_count = 0

            for el in find_els(div, 'p'):
                el_count += 1
                result.append(el)

        return result

    def append_subtitle(self, from_ms, to_ms, content, new_paragraph=False,
                        escape=True):
        """Append a subtitle to the end of the list.

        NO UNICODE ALLOWED!  USE XML ENTITIES TO REPRESENT UNICODE CHARACTERS!

        """

        if escape:
            content = escape_xml(content)
        content = self._fix_xml_content(content)
        p = self._create_subtitle_p(from_ms, to_ms, content)

        if new_paragraph:
            div = etree.SubElement(self._body, TTML + 'div')
        else:
            div = self.last_div()
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
        if dur :
            end= milliseconds_to_time_clock_exp(
                time_expression_to_milliseconds(begin, self.tick_rate) + \
                time_expression_to_milliseconds(dur, self.tick_rate))
            el.attrib.pop('dur')
        if begin:
            el.attrib['begin'] = begin
        if end:
            el.attrib['end'] = end

    def subtitle_items(self, mappings=None):
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
                NEW_PARAGRAPH_META_KEY: True if el.getprevious()is None  else False
            }
            result.append(self._extract_from_el(el, meta, mappings))

        self.subtitles = result
        return result

    def _extract_from_el(self, el, meta, mappings):
        begin = get_attr(el, 'begin')
        end = get_attr(el, 'end')


        from_ms = (time_expression_to_milliseconds(begin)
                if begin  is not None and begin is not '' else None)
        to_ms = (time_expression_to_milliseconds(end)
                if end is not None and end is not '' else None)
        if not mappings:
            content = get_contents(el)
        else:
            content = self.get_content_with_markup(el, mappings)

        return SubtitleLine(from_ms, to_ms, content, meta)

    def __clear_namespace(self, name):
        return name.split("}")[-1] if '}' in name else name

    def item_is_synced(self, el):
        begin = el.attrib.get('begin', None)
        end = el.attrib.get('end', None)
        return begin is not None and begin.strip() != '' and \
               end is not None and end.strip() != ''

    @property
    def fully_synced(self):
        for item in self.get_subtitles():
            if not self.item_is_synced(item):
                return False
        return True

    def get_content_with_markup(self, el, mappings):
        return self._get_content_with_markup(el, mappings).strip()

    def _get_content_with_markup(self, el, mappings):
        quote_text = mappings.get('quote_text', lambda x: x)
        text = []
        if el.text:
            text.append(quote_text(el.text))
        for child in el:
            tag = self.__clear_namespace(element_tag(child))

            if tag == 'span':
                template = self._template_for_span(child, mappings)
                text.append(template %
                            (self._get_content_with_markup(child, mappings),))

            elif tag == "br":
                if 'linebreaks' in mappings:
                    text.append(mappings['linebreaks'])

            if child.tail:
                text.append(quote_text(child.tail))

        return ''.join(text)

    def _template_for_span(self, elt, mappings):
        """String to use for a span for get_content_with_markup().

        The returned string will contain a single "%s" value to be filled in
        with the contents of the span.
        """
        # no i don't want to deal with namespaces right now sorry
        attrs = dict([(self.__clear_namespace(n), v)
                      for n, v in elt.items()])

        template = "%s"
        if attrs.get('fontWeight', '') == 'bold' and 'bold' in mappings:
            template = template % mappings.get("bold", "")

        if attrs.get('fontStyle', '') == 'italic' and 'italics' in mappings:
            template = template % mappings.get("italics", "")

        if attrs.get('textDecoration', '') == 'underline' and 'underline' in mappings:
            template = template % mappings.get("underline", "")
        return template

    def update(self, subtitle_index, from_ms=None, to_ms=None):
        """Updates the subtitle on index subtitle_index with the
        new timing data. (in place)

        If you need to update timing to mark as the unsynced value use
        utils.UNSYNCED_TIME_FULL  as the value to pass
        TODO: Implement content change (beware of escaping
        """
        el = self.get_subtitles()[subtitle_index]
        if from_ms is not None:
            el.set('begin',   milliseconds_to_time_clock_exp(from_ms) )
        if to_ms is not None:
            el.set('end',  milliseconds_to_time_clock_exp(to_ms) )

    def set_language(self, language_code):
        self._ttml.set(XML + 'lang', language_code)

    @classmethod
    def from_list(cls, language_code, subtitles, escape=False):
        """Return a SubtitleSet from a list of subtitle tuples.

        Each tuple should be (from_ms, to_ms, content).  See the docstring of
        append_subtitle for more information.

        For example:

            [(0, 1000, "Hello, ", {'new_paragraph':True}),
             (1100, None, "world!")]

        """
        subs = SubtitleSet(language_code=language_code)


        for s in subtitles:
            extra = {}
            if len(s) > 3:
               extra = s[3]
               s = s[:-1]
            extra['escape'] = escape
            subs.append_subtitle( *s, **extra)
        return subs

    def _get_tick_rate(self):
        try:
            tt = self.find_divs()[0]
        except IndexError as e:
            from babelsubs.parsers.base import SubtitleParserError
            raise SubtitleParserError(
                "No valid root elements found, we'll accept 'tt, body and div",
                original_error=e)
        for name,value in tt.attrib.items():
            if name == "tickRate":
                return int(value)
        return 1
 
    def __eq__(self, other):
        if type(self) == type(other):
            return not diff(self, other, None)['changed']
        else:
            return False

    def __nonzero__(self):
        return bool(self.__len__())

    def validate(self):
        raise NotImplementedError("Validation isnt working so far")

    def to_xml(self):
        return etree.tostring(self._ttml)

    def as_etree_node(self):
        return copy.deepcopy(self._ttml)
