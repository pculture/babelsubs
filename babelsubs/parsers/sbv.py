import re
from babelsubs import utils

from base import BaseTextParser, register

class SBVParser(BaseTextParser):

    file_type = 'sbv'

    def __init__(self, input_string, language=None):
        pattern = r'(?P<s_hour>\d{1}):(?P<s_min>\d{2}):(?P<s_sec>\d{2})\.(?P<s_secfr>\d{3})'
        pattern += r','
        pattern += r'(?P<e_hour>\d{1}):(?P<e_min>\d{2}):(?P<e_sec>\d{2})\.(?P<e_secfr>\d{3})'
        pattern += r'\n(?P<text>.+?)\n\n'
        input_string = utils.strip_tags(input_string)
        super(SBVParser, self).__init__(input_string, pattern, flags=[re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.input_string = self.input_string.replace('\r\n', '\n')+u'\n\n'
        self.language = language

    def _get_time(self, hour, min, sec, secfr):
        if secfr is None:
            secfr = '0'
        res  =  (int(hour)*60*60+int(min)*60+int(sec)+float('.'+secfr)) * 1000
        return res

    def _get_data(self, match):
        r = match.groupdict()
        output = {}
        output['start'] = self._get_time(r['s_hour'], r['s_min'], r['s_sec'], r['s_secfr'])
        output['end'] = self._get_time(r['e_hour'], r['e_min'], r['e_sec'], r['e_secfr'])
        # [br] are linebreaks:
        text = '' if r['text'] is None else r['text']
        text = text.replace("[br]", "<br/>")
        output['text'] = text
        return output


register(SBVParser)
