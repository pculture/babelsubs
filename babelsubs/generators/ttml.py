import re
import xml.dom.minidom

from math import floor
from babelsubs.utils import to_bcp47
from babelsubs.generators.base import BaseGenerator, register

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

register(TTMLGenerator)
