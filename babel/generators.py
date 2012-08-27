import codecs
import xml.dom.minidom

from HTMLParser import HTMLParser
from math import floor

from utils import to_bcp47

class GeneratorListClass(dict):

    def register(self, handler, type=None):
        self[type or handler.file_type] = handler

    def __getitem__(self, item):
        return self.get(item, None)

GeneratorList = GeneratorListClass()

class BaseGenerator(object):
    file_type = ''

    def __init__(self, subtitles, line_delimiter=u'\n', language=None):
        """
        Generator is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds'}
        """
        self.subtitles = subtitles
        self.line_delimiter = line_delimiter
        self.language = language

    def __unicode__(self):
        raise Exception('Should return subtitles')

    @classmethod
    def isnumber(cls, val):
        return isinstance(val, (int, long, float))

    @classmethod
    def generate(cls, subtitles, language=None):
        return unicode(cls(subtitles=subtitles, language=language))

class SRTGenerator(BaseGenerator):
    file_type = 'srt'

    def __init__(self, subtitles, line_delimiter=u'\r\n', language=None):
        super(SRTGenerator, self).__init__(subtitles, line_delimiter)

    def __unicode__(self):
        output = []

        parser = HTMLParser()
        i = 1
        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                output.append(unicode(i))
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                output.append(u'%s --> %s' % (start, end))
                output.append(parser.unescape(item['text']).strip())
                output.append(u'')
                i += 1

        return self.line_delimiter.join(output)

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 99
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%02i:%02i:%02i,%03i' % (hours, minutes, seconds, fr_seconds)


class SBVGenerator(BaseGenerator):
    file_type = 'sbv'

    def __init__(self, subtitles,  line_delimiter=u'\r\n', language=None):
        super(SBVGenerator, self).__init__(subtitles, line_delimiter)

    def __unicode__(self):
        output = []

        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                output.append(u'%s,%s' % (start, end))
                output.append(item['text'].strip())
                output.append(u'')

        return self.line_delimiter.join(output)

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 9
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 1000)
        return u'%01i:%02i:%02i.%03i' % (hours, minutes, seconds, fr_seconds)


class TXTGenerator(BaseGenerator):
    file_type = 'txt'

    def __init__(self, subtitles, line_delimiter=u'\r\n\r\n', language=None):
        super(TXTGenerator, self).__init__(subtitles, line_delimiter)

    def __unicode__(self):
        output = []
        for item in self.subtitles:
            item['text'] and output.append(item['text'].strip())

        return self.line_delimiter.join(output)


class SSAGenerator(BaseGenerator):
    file_type = 'ssa'

    def __unicode__(self):
        #add BOM to fix python default behaviour, because players don't play without it
        return u''.join([unicode(codecs.BOM_UTF8, "utf8"), self._start(), self._content(), self._end()])

    def _start(self):
        ld = self.line_delimiter
        return u'[Script Info]%sTitle: %s%s' % (ld, getattr(self, 'title', ''), ld)

    def _end(self):
        return u''

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 9
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%i:%02i:%02i.%02i' % (hours, minutes, seconds, fr_seconds)

    def _clean_text(self, text):
        return text.replace('\n', ' ')

    def _content(self):
        dl = self.line_delimiter
        output = []
        output.append(u'[Events]%s' % dl)
        output.append(u'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text%s' % dl)
        tpl = u'Dialogue: 0,%s,%s,Default,,0000,0000,0000,,%s%s'
        for item in self.subtitles:
            if self.isnumber(item['start']) and self.isnumber(item['end']):
                start = self.format_time(item['start'])
                end = self.format_time(item['end'])
                text = self._clean_text(item['text'].strip())
                output.append(tpl % (start, end, text, dl))
        return ''.join(output)


import re

class TTMLGenerator(BaseGenerator):
    file_type = 'xml'
    remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
    use_named_styles = True
    STYLES = {

        "strong": {
            'fontWeight':'bold'
        },
        'emphasis': {
            'textStyle': 'italic'
        },
        'underlined': {
            'textDecoration': 'underline'
        }
    }

    def __unicode__(self):
        node = self.xml_node()
        return node.toxml()

    def _get_attributes(self, item):
        attrib = {}
        attrib['begin'] = self.format_time(item['start'])
        attrib['dur'] = self.format_time(item['end']-item['start'])
        return attrib

    def xml_node(self):
        xmlt = """<tt xml:lang="%s" xmlns="http://www.w3.org/ns/ttml"
                      xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
                      xmlns:tts="http://www.w3.org/ns/ttml#styling" >
        <head>
            <metadata/>
            <styling/>
            <layout/>
        </head>
        <body region="subtitleArea">
            <div>
            </div>
        </body>
        </tt>""" % to_bcp47(self.language)
        from xml.dom import expatbuilder
        dom = xml.dom.minidom.parseString(xmlt)
	styling = dom.getElementsByTagName('head')[0].getElementsByTagName('styling')[0]
        styling.setAttribute("xmlns:tts", "http://www.w3.org/2006/10/ttaf1#styling")

        for style_name, style_def in TTMLGenerator.STYLES.items():
            style = dom.createElement('style')
            style.setAttribute('xml:id', style_name)
            for def_name, def_style in style_def.items():
                style.setAttribute(def_name, def_style)
            styling.appendChild(style)

	div = dom.getElementsByTagName('tt')[0].getElementsByTagName('body')[0].getElementsByTagName('div')[0]
        italic_declaration = 'tts:fontStyle="italic"' if TTMLGenerator.use_named_styles else 'style="emphasis"'
        bold_declaration = 'tts:fontWeight="bold"' if TTMLGenerator.use_named_styles else 'style="strong"'
        underline_declaration = 'tts:textDecoration="underline"' if TTMLGenerator.use_named_styles else 'style="underlined"'
            
        for i,item in enumerate(self.subtitles):
            if item['text'] and self.isnumber(item['start']) and self.isnumber(item['end']):
                # as we're replacing new lines with <br>s we need to create
                # the element from a fragment,and also from the formateed <b> and <i> to
                # the correct span / style
                content = item['text'].replace(u'\n', u'<br/>').strip()
                content = content.replace(u"<b>", u'<span  %s>' % (bold_declaration)).replace(u"</b>", u'</span>')
                content = content.replace(u"<i>", u'<span  %s>' % (italic_declaration)).replace(u"</i>", u'</span>')
                content = content.replace(u"<u>", u'<span  %s>' % (underline_declaration)).replace(u"</u>", u'</span>')
                xml_str = (u'<p xml:id="sub-%s">%s</p>' % (i,content)).encode('utf-8')
        
                # we need to use this parser to make sure namespace chekcing is off
                # else the node can't be generated without the proper context
                node = expatbuilder.parseString(xml_str, namespaces=False)
                child = node.documentElement

                for k,v in self._get_attributes(item).items():
                    child.setAttribute(k,v)
                div.appendChild(child)

        return dom

    def format_time(self, time):
        hours = int(floor(time / 3600))
        if hours < 0:
            hours = 99
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%02i:%02i:%02i.%02i' % (hours, minutes, seconds, fr_seconds)


class DFXPGenerator(TTMLGenerator):
    file_type = 'dfxp'

    def _get_attributes(self, item):
        attrib = {}
        attrib['begin'] = self.format_time(item['start'])
        attrib['end'] = self.format_time(item['end'])
        return attrib

GeneratorList.register(SSAGenerator)
GeneratorList.register(TXTGenerator)
GeneratorList.register(SBVGenerator)
GeneratorList.register(SRTGenerator)
GeneratorList.register(DFXPGenerator)
GeneratorList.register(TTMLGenerator)

def discover(type):
    return GeneratorList[type]
