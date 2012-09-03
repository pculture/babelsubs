from babelsubs import utils
from babelsubs.storage import SubtitleSet
from base import BaseTextParser, SubtitleParserError, register
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

MAX_SUB_TIME = (60 * 60 * 100) - 1

class DFXPParser(BaseTextParser):

    file_type = 'dfxp'

    def __init__(self, subtitles, language=None):
        try:
            # do not pass utf-8 econded strings. If the xml declaration is
            # something else, the parser will complain otherwise
            dom = parseString(subtitles)
            self.style_map = utils.generate_style_map(dom)
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
            'text': utils.unescape_html(utils.from_xmlish_text(node.toxml()))
        }
        output['start'] = self._get_time(node.getAttribute('begin'))
        output['end'] = self._get_time(node.getAttribute('end'))

        return output

    def _result_iter(self):
        for item in self.nodes:
            yield self._get_data(item)

    def to_internal(self):
        if not hasattr(self, 'sub_set'):
            self.sub_set = SubtitleSet(self.language)
            for node in self.nodes:
                item = self._get_data(node)
                self.sub_set.append_subtitle(item['start'], item['end'],
                        item['text'])

        return self.sub_set


register(DFXPParser)
