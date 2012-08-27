from babel import utils
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from base import BaseParser, SubtitleParserError, register

MAX_SUB_TIME = (60 * 60 * 100) - 1

class TTMLParser(BaseParser):

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
            'text': utils.unescape_html(utils.from_xmlish_text(node.toxml()))
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

register(TTMLParser)
