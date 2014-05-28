import re
import bleach
import htmllib
import htmlentitydefs
import formatter

from itertools import chain
from xmlconst import *

DEFAULT_ALLOWED_TAGS = ['i', 'b', 'u']
MULTIPLE_SPACES = re.compile('\s{2,}')
BLANK_CHARS = re.compile('[\n\t\r]*')
# We support unsyced subs, meaning there is not timing data for them
# in which case we flag them with the largest possible time value
UNSYNCED_TIME_FULL = (60 * 60 * 100 * 1000) - 1
# some formats limit hours to 1 digit, so the max available time must
# be adjusted
UNSYNCED_TIME_ONE_HOUR_DIGIT = (60 * 60 * 10 * 1000) - 1000

def unescape_html(s):
    p = htmllib.HTMLParser(formatter.NullFormatter() )
    # we need to preserve line breaks, nofill makes sure we don't
    # loose them
    p.nofill = True
    p.save_bgn()
    p.feed(s)
    return p.save_end().strip()

LANG_DIALECT_RE = re.compile(r'(?P<lang_code>[\w]{2,13})(?P<dialect>-[\w]{2,8})?(?P<rest>-[\w]*)?')

def to_bcp47(code):
    """
    This is an ugly hack. I should be ashamed, but I'm not.
    Implementing BCP47 will be much more work.
    The idea is to translate from a lang code unilangs supports
    into the bpc47 format. There are cases where this might fail
    (as if the dialect code is not recognized by bcp47). For most cases this should be ok.

    Simple sanity chech:
    assert (unilangs.to_bcp47("en-us"), unilangs.to_bcp47('en'), unilangs.to_bcp47('ug_Arab-cn')) == ('en-US', 'en', 'ug_Arab-CN'
)
    """
    if not code:
         raise ValueError("No language was passed")

    match = LANG_DIALECT_RE.match(code)
    if not match:
         raise ValueError("%s code does not seem to be a valid language code.")

    match_dict = match.groupdict()
    return "%s%s%s" % (match_dict['lang_code'],
                       (match_dict.get('dialect', "") or "").upper(),
                       match_dict.get('rest', '') or "")

def generate_style_map(dom):
    '''
    Parse the head.styling node on the xml and generate a hash -> list
    of styles that require our supported formatting optins (bold and
    italic for now).
    eg.
    style_map = {
        'italic': ['speaker', 'importante'],
        'bold': [],
    }
    This will be used when parsing each text node to make sure
    we can convert to our own styling markers.
    '''
    style_map = {
        'italic': [],
        'bold': [],
    }
    styling_nodes = dom.getElementsByTagName("styling")
    style_nodes = chain.from_iterable([x.getElementsByTagName('style') for x in styling_nodes])
    for style_node in style_nodes:
        style_id = style_node.getAttribute('xml:id')
        for key in style_node.attributes.keys():
            value  = style_node.attributes[key].value
            if key  == 'tts:fontWeight' and  value == 'bold':
                style_map['bold'].append(style_id)
            elif key  == 'tts:fontStyle' and value == 'italic':
                style_map['italic'].append(style_id)
    return style_map

def strip_tags(text, tags=None):
    """
    Returns text with the tags stripped.
    By default we allow the standard formatting tags
    to pass (i,b,u).
    Any other tag's content will be present, but with tags removed.
    """
    if tags is None:
        tags = DEFAULT_ALLOWED_TAGS
    return bleach.clean(text, tags=tags, strip=True)


def escape_ampersands(text):
    """Take a string of chars and replace ampersands with &amp;"""
    return text.replace('&', '&amp;')

def entities_to_chars(text):
    """Removes HTML or XML character references and entities from a text string.

    http://effbot.org/zone/re-sub.htm#unescape-html

    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def from_xmlish_text(input_str):
    """
    Parses text content from xml based formats.
    <br> tags are transformed into newlines, tab and multiple spaces
    collapsed. e.g. turns:
    "\n\r foo  <br/> bar foorer \t " -> "foo bar\nfoorer"
    """
    if not input_str:
        return u""
    # remove new lines and tabs
    input_str = BLANK_CHARS.sub(u"", input_str)
    # do convert <br> to new lines
    input_str = input_str.replace("<br/>", "\n")
    # collapse whitespace on each new line
    return "\n".join( MULTIPLE_SPACES.sub(u" ", x).strip() for x in input_str.split('\n'))

def unsynced_time_components(one_hour_digit=False, uses_centiseconds=False):
    return {
        'hours': 9 if one_hour_digit else 99,
        'minutes': 59,
        'seconds': 59,
        'milliseconds': 99 if uses_centiseconds else 999,
        'centiseconds': 99,
    }
def milliseconds_to_time_clock_components(milliseconds,
                                          unsynced_val=UNSYNCED_TIME_FULL,
                                          use_centiseconds=False):
    """Convert milliseconds to a dict of hours, minutes, seconds, milliseconds.

    Milliseconds should be given as an integer, or None.  None will be converted
    to all zeros.

    If use_centiseconds is True, the resulting dict will have a centiseconds
    entry instead of a milliseconds one.

    """
    components = dict(hours=0, minutes=0, seconds=0, milliseconds=0)

    if milliseconds is not None:
        components['seconds'], components['milliseconds'] = divmod(int(milliseconds), 1000)
        components['minutes'], components['seconds'] = divmod(components['seconds'], 60 )
        components['hours'], components['minutes'] = divmod(components['minutes'], 60 )

    if use_centiseconds:
        ms = components.pop('milliseconds')
        components['centiseconds'] = round(ms / 10.0)

    return components

def fraction_to_milliseconds(str_milli):
    """
    Converts milliseonds as an integer string to a 3 padded string, e.g.
    1 -> 001
    10 -> 010
    100 -> 100
    """
    if not str_milli:
        return 0
    return int(str_milli.ljust(3, '0')) % 1000


def centiseconds_to_milliseconds(centi):
    return int(centi) * 10 if centi else 0

def indent_ttml(tt_elt, indent_width=4):
    """Indent TTML tree

    This function walks the XML tree and adjusts the text and tail attributes
    so that the output will be nicely indented.  It skips <p> elements and
    their children, since whitespace is significant there.

    Also, we will add a newline after the closing tag for the TT element.

    :param tt_elt: etree TT root element.
    """
    _do_indent_ttml(tt_elt, " " * indent_width, 0)
    tt_elt.tail = "\n"

def _do_indent_ttml(elt, indent, indent_level):
    if elt.tag == TTML + 'p' or len(elt) == 0:
        return
    children = list(elt)

    # before a child element, we want to start a new line, then indent enough
    # to move them to the next indentation level
    pre_child_indent = "\n" + indent * (indent_level + 1)

    elt.text = pre_child_indent
    for child in children[:-1]:
        child.tail = pre_child_indent
    # after the last child, we need to position our closing tag.  This means
    # indenting enough to move it to our indentation level.
    children[-1].tail = "\n" + indent * indent_level

    for child in children:
        _do_indent_ttml(child, indent, indent_level + 1)
