import re

from babelsubs import utils
from babelsubs.parsers.base import BaseTextParser, register

class WEBVTTParser(BaseTextParser):

    file_type = 'vtt'
    _clean_pattern = re.compile(r'\{.*?\}', re.DOTALL)

    def __init__(self, input_string, language_code, eager_parse=True):
        pattern = r'((?P<s_hour>\d{2}):)?(?P<s_min>\d{2}):(?P<s_sec>\d{2})(.(?P<s_secfr>\d*))?'
        pattern += r' --> '
        pattern += r'((?P<e_hour>\d{2}):)?(?P<e_min>\d{2}):(?P<e_sec>\d{2})(.(?P<e_secfr>\d*))?'
        pattern += r'([ \t]+(?P<cue_settings>[^\r\n]+))?'
        pattern += r'\n(\n|(?P<text>.+?)\n\n)'
        input_string = input_string.replace('\r\n', '\n').replace('\r', '\n')+'\n\n'
        super(WEBVTTParser, self).__init__(input_string, pattern, language=language_code,
            flags=[re.DOTALL], eager_parse=eager_parse)


    def _get_time(self, hour, min, sec, milliseconds):
        if hour is None:
            hour = 0
        if milliseconds is None:
            milliseconds = '0'
        res  =  (int(hour)*60*60+int(min)*60+int(sec)+float('.'+milliseconds)) * 1000
        if res == utils.UNSYNCED_TIME_FULL:
            res = None
        return res

    def _get_data(self, match):
        output = {}
        output['start'] = self._get_time(match['s_hour'],
                                         match['s_min'],
                                         match['s_sec'],
                                         match['s_secfr'])
        output['end'] = self._get_time(match['e_hour'],
                                       match['e_min'],
                                       match['e_sec'],
                                       match['e_secfr'])
        text = ('' if match['text'] is None else
                utils.escape_ampersands(utils.strip_tags(
                    self._clean_pattern.sub('', match['text'])))
               )
        output['text'] = self.get_markup(text)
        cue_settings = self._parse_cue_settings(match['cue_settings'])
        output['region'] = self.calc_region(cue_settings)
        return output

    def _parse_cue_settings(self, settings_text):
        if settings_text is None:
            return {}
        return dict(s.split(':', 1) for s in settings_text.split())

    def calc_region(self, cue_settings):
        line = cue_settings.get('line')
        if not line:
            return None
        # remove alignment if present at the end ("1,start")
        line = line.split(',', 1)[0]
        if line.endswith('%'):
            return self.calc_region_percent(line)
        else:
            return self.calc_region_number(line)

    def calc_region_percent(self, line):
        try:
            percent = int(line[:-1])
        except ValueError:
            return None
        if percent <= 20:
            return 'top'
        else:
            return None

    def calc_region_number(self, line):
        try:
            number = int(line)
        except ValueError:
            return None
        if 0 <= number <= 5:
            return 'top'
        else:
            return None

register(WEBVTTParser)
