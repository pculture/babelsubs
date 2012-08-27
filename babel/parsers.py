import re
import bleach

from itertools import chain

from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from babel.utils import unescape_html

from babel import generators

DEFAULT_ALLOWED_TAGS = ['i', 'b', 'u']
MULTIPLE_SPACES = re.compile('\s{2,}')
BLANK_CHARS = re.compile('[\n\t\r]*')
MAX_SUB_TIME = (60 * 60 * 100) - 1

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
 

class SubtitleParserError(Exception):
    pass

class ParserListClass(dict):
    def register(self, parser, file_type):
        if not isinstance(file_type, (basestring, list)):
            raise Exception("File_type must be a string or a list")

        if isinstance(file_type, list):
            for ft in file_type:
                self[ft] = parser
        else:
            self[file_type] = parser

    def __getitem__(self, item):
        return self.get(item, None)

    def extensions(self):
        keys = sorted(ParserList.keys())
        extensions = ['.'+k for k in keys[:-1]]
        last = "."+keys[-1]

        return ", ".join(extensions) + " or %s" % last

ParserList = ParserListClass()

class SubtitleParser(object):

    def __init__(self, subtitles, pattern, language=None, flags=[]):
        self.subtitles = subtitles
        self.pattern = pattern
        self.language = language
        self._pattern = re.compile(pattern, *flags)

    def __iter__(self):
        return self._result_iter()

    def __len__(self):
        return len(self._pattern.findall(self.subtitles))

    def __nonzero__(self):
        return bool(self._pattern.search(self.subtitles))

    def _result_iter(self):
        """
        Should iterate over items like this:
        {
            'start': ...,
            'end': ...,
            'text': ...
        }
        start_time and end_time in seconds. If it is not defined use -1.
        """
        for item in self._matches:
            yield self._get_data(item)

    def _get_data(self, match):
        return match.groupdict()

    def _get_matches(self):
        return self._pattern.finditer(self.subtitles)

    @classmethod
    def parse(cls, subtitles, language=None):
        return cls(subtitles, language)

    def to(self, type):
        generator = generators.discover(type)

        if not generator:
            raise TypeError("Could not find a type %s" % type)

        return generator.generate(self._result_iter(), language=self.language)

    _matches = property(_get_matches)


class TxtSubtitleParser(SubtitleParser):

    file_type = 'txt'

    _linebreak_re = re.compile(r"\n\n|\r\n\r\n|\r\r")

    def __init__(self, subtitles, language=None, linebreak_re=_linebreak_re):
        self.subtitles = linebreak_re.split(subtitles, language)

    def __len__(self):
        return len(self.subtitles)

    def __nonzero__(self):
        return bool(self.subtitles)

    def _result_iter(self):
        for item in self.subtitles:
            output = {}
            output['start'] = -1
            output['end'] = -1
            output['text'] = strip_tags(item)
            yield output

class STSubtitleParser(SubtitleParser):

    def __init__(self, subtitles, language=None):
        try:
            dom = parseString(subtitles.encode('utf8'))
            self.nodes = dom.getElementsByTagName('transcript')[0].getElementsByTagName('content')
            self.language = language
        except (ExpatError, IndexError):
            raise SubtitleParserError('Incorrect format of SpeakerText subtitles')


    def __len__(self):
        return len(self.nodes)

    def __nonzero__(self):
        return bool(len(self.nodes))

    def _get_time(self, val):
        try:
            return int(val) / 1000.
        except ValueError:
            return -1

    def _get_data(self, node):

        output = {
            'text': strip_tags(strip_tags(node.toxml()).strip())
        }
        output['start'] = self._get_time(node.getAttribute('timestamp'))
        output['end'] = self._get_time(node.getAttribute('end_timestamp'))

        return output

    def _result_iter(self):
        for item in self.nodes:
            yield self._get_data(item)

class TtmlSubtitleParser(SubtitleParser):

    file_type = ['xml', 'ttml']

    def __init__(self, subtitles, language=None):
        try:
            # do not pass utf-8 econded strings. If the xml declaration is
            # something else, the parser will complain otherwise
            dom = parseString(subtitles)
            self.nodes = dom.getElementsByTagName('body')[0].getElementsByTagName('p')
            self.language = language
        except (ExpatError, IndexError):
            raise SubtitleParserError('Incorrect format of TTML subtitles')
                       

    def __len__(self):
        return len(self.nodes)

    def __nonzero__(self):
        return bool(len(self.nodes))

    def _get_time(self, begin, dur, is_duration=True):
        if not begin or not dur:
            return -1

        try:
            hour, min, sec = begin.split(':')

            start = int(hour)*60*60 + int(min)*60 + float(sec)
            if start > MAX_SUB_TIME:
                return -1

            d_hour, d_min, d_sec = dur.split(':')
            end =  + int(d_hour)*60*60 + int(d_min)*60 + float(d_sec)
            if is_duration:
                end += start
        except ValueError:
            return -1

        return start, end

    def _get_data(self, node):

        output = {
            'text': unescape_html(from_xmlish_text(node.toxml()))
        }
        if node.hasAttribute('dur'):
            output['start'], output['end'] = \
                self._get_time(node.getAttribute('begin'), node.getAttribute('dur'))
        else:
            output['start'], output['end'] = \
                self._get_time(node.getAttribute('begin'), node.getAttribute('end'), False)
        return output

    def _result_iter(self):
        for item in self.nodes:
            yield self._get_data(item)

class DfxpSubtitleParser(SubtitleParser):

    file_type = 'dfxp'

    def __init__(self, subtitles, language=None):
        try:
            # do not pass utf-8 econded strings. If the xml declaration is
            # something else, the parser will complain otherwise
            dom = parseString(subtitles)
            self.style_map = generate_style_map(dom)
            t = dom.getElementsByTagName('tt')[0]
            
            self.tickRate = 0;
            
            for attr in t.attributes.values():
                if attr.localName == "tickRate":
                    self.tickRate = int(attr.value)
                        
            self.nodes = dom.getElementsByTagName('body')[0].getElementsByTagName('p')
            self.language = language
        except (ExpatError, IndexError):
            raise SubtitleParserError('Incorrect format of TTML subtitles')

    def __len__(self):
        return len(self.nodes)

    def __nonzero__(self):
        return bool(len(self.nodes))

    def _get_time(self, t):
        try:
            if t.endswith('t'):
                ticks = int(t.split('t')[0])
            
                start = ticks / float(self.tickRate)
            
            else:
                hour, min, sec = t.split(':')
            
                start = int(hour)*60*60 + int(min)*60 + float(sec)
                if start > MAX_SUB_TIME:
                    return -1
        except ValueError:
            return -1

        return start

    def _replace_els(self, node, attrname, attrvalue, tagname):
        """
        Edits the node in place, changing <span:[attrname]=[attrvalue]>x</span> to 
        <[tagname]>x</tagname>
        This is needed because in order to store the markkup like
        format we use internally, we need to convert the dfxp specific
        tags to the regural htmlishy tags we use.
        """
        els = [x for x in node.childNodes if hasattr(x, 'tagName') and x.tagName == 'span' and x.getAttribute(attrname) == attrvalue]
        for x  in els:
            x.tagName = tagname
            # if you have text like <i>hey, </i><span>you</span>, the markdown processor
            # will get confused (it needs to see *hey,* , not *hey, * .
            # this ugly hack shifts the space to the beginning of the next node. will probably
            # break under various other edge cases. Ideas?
            if x.firstChild and len(x.firstChild.nodeValue.rstrip()) != x.firstChild.nodeValue and x.nextSibling:
                x.firstChild.nodeValue = x.firstChild.nodeValue.rstrip()
                if x.nextSibling and x.nextSibling.firstChild and not x.nextSibling.firstChild.nodeValue.startswith(" "):
                    x.nextSibling.firstChild.nodeValue = " " + x.nextSibling.firstChild.nodeValue
            x.removeAttribute(attrname)

    def _get_data(self, node):
        # replace inline styles to our markdown format, e.g.
        # <span fontWeith='bold'> -> **
        self._replace_els(node, 'tts:fontStyle', 'italic', 'i')
        self._replace_els(node, 'tts:fontWeight', 'bold', 'b')
        # now look at names styles. go over the style map for this
        # data and if the style matches one of ours, replace it
        for style_name in self.style_map['bold']:
            self._replace_els(node, 'style', style_name, 'b')
        for style_name in self.style_map['italic']:
            self._replace_els(node, 'style', style_name, 'i')
            

        output = {
            'text': unescape_html(from_xmlish_text(node.toxml()))
        }
        output['start'] = self._get_time(node.getAttribute('begin'))
        output['end'] = self._get_time(node.getAttribute('end'))

        return output

    def _result_iter(self):
        for item in self.nodes:
            yield self._get_data(item)

class SrtSubtitleParser(SubtitleParser):

    file_type = 'srt'
    _clean_pattern = re.compile(r'\{.*?\}', re.DOTALL)

    def __init__(self, subtitles, language=None):
        pattern = r'\d+\s*?\n'
        pattern += r'(?P<s_hour>\d{2}):(?P<s_min>\d{2}):(?P<s_sec>\d{2})(,(?P<s_secfr>\d*))?'
        pattern += r' --> '
        pattern += r'(?P<e_hour>\d{2}):(?P<e_min>\d{2}):(?P<e_sec>\d{2})(,(?P<e_secfr>\d*))?'
        pattern += r'\n(\n|(?P<text>.+?)\n\n)'
        super(SrtSubtitleParser, self).__init__(subtitles, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+'\n\n'
        self.language = language

    def _get_time(self, hour, min, sec, secfr):
        if secfr is None:
            secfr = '0'
        return int(hour)*60*60+int(min)*60+int(sec)+float('.'+secfr)

    def _get_data(self, match):
        r = match.groupdict()
        output = {}
        output['start'] = self._get_time(r['s_hour'], r['s_min'], r['s_sec'], r['s_secfr'])
        output['end'] = self._get_time(r['e_hour'], r['e_min'], r['e_sec'], r['e_secfr'])
        output['text'] = '' if r['text'] is None else \
            strip_tags(self._clean_pattern.sub('', r['text']))
        return output

class SbvSubtitleParser(SrtSubtitleParser):

    file_type = 'sbv'

    def __init__(self, subtitles, language=None):
        pattern = r'(?P<s_hour>\d{1}):(?P<s_min>\d{2}):(?P<s_sec>\d{2})\.(?P<s_secfr>\d{3})'
        pattern += r','
        pattern += r'(?P<e_hour>\d{1}):(?P<e_min>\d{2}):(?P<e_sec>\d{2})\.(?P<e_secfr>\d{3})'
        pattern += r'\n(?P<text>.+?)\n\n'
        subtitles = strip_tags(subtitles)
        super(SrtSubtitleParser, self).__init__(subtitles, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+u'\n\n'
        self.language = language

class SsaSubtitleParser(SrtSubtitleParser):

    file_type = ['ssa', 'ass']

    def __init__(self, file, language=None):
        pattern = r'Dialogue: [\w=]+,' #Dialogue: <Marked> or <Layer>,
        pattern += r'(?P<s_hour>\d):(?P<s_min>\d{2}):(?P<s_sec>\d{2})[\.\:](?P<s_secfr>\d+),' #<Start>,
        pattern += r'(?P<e_hour>\d):(?P<e_min>\d{2}):(?P<e_sec>\d{2})[\.\:](?P<e_secfr>\d+),' #<End>,
        pattern += r'[\w ]+,' #<Style>,
        pattern += r'[\w ]*,' #<Character name>,
        pattern += r'\d{4},\d{4},\d{4},' #<MarginL>,<MarginR>,<MarginV>,
        pattern += r'[\w ]*,' #<Efect>,
        pattern += r'(?:\{.*?\})?(?P<text>.+?)\n' #[{<Override control codes>}]<Text>
        super(SrtSubtitleParser, self).__init__(file, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+u'\n'
        self.language = language

ParserList.register(SrtSubtitleParser, 'srt')
ParserList.register(SsaSubtitleParser, ['ssa', 'ass'])
ParserList.register(TtmlSubtitleParser, ['xml', 'ttml'])
ParserList.register(SbvSubtitleParser, 'sbv')
ParserList.register(DfxpSubtitleParser, 'dfxp')
ParserList.register(TxtSubtitleParser, 'txt')

def discover(type):
    return ParserList[type]
