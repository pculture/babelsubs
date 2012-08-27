import re

from babel import utils
from base import BaseParser, register

class SRTParser(BaseParser):

    file_type = 'srt'
    _clean_pattern = re.compile(r'\{.*?\}', re.DOTALL)

    def __init__(self, subtitles, language=None):
        pattern = r'\d+\s*?\n'
        pattern += r'(?P<s_hour>\d{2}):(?P<s_min>\d{2}):(?P<s_sec>\d{2})(,(?P<s_secfr>\d*))?'
        pattern += r' --> '
        pattern += r'(?P<e_hour>\d{2}):(?P<e_min>\d{2}):(?P<e_sec>\d{2})(,(?P<e_secfr>\d*))?'
        pattern += r'\n(\n|(?P<text>.+?)\n\n)'
        super(SRTParser, self).__init__(subtitles, pattern, [re.DOTALL])
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
            utils.strip_tags(self._clean_pattern.sub('', r['text']))
        return output

register(SRTParser)
