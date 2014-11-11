import re

from base import BaseTextParser, register
from babelsubs import utils

class SBVParser(BaseTextParser):

    file_type = 'sbv'

    def __init__(self, input_string, language=None, eager_parse=True):
        pattern = r'(?P<s_hour>\d{1}):(?P<s_min>\d{2}):(?P<s_sec>\d{2})\.(?P<s_secfr>\d{3})'
        pattern += r','
        pattern += r'(?P<e_hour>\d{1}):(?P<e_min>\d{2}):(?P<e_sec>\d{2})\.(?P<e_secfr>\d{3})'
        pattern += r'\n(?P<text>.+?)\n\n'
        # TODO: Support the DELAY header. Now, how can we map frames
        # to time coordinates without having a frame rate number?
        # My guess people expect it to be guessable through the video
        # file, but that renders our quest useless. Ideas?
        input_string = input_string.replace('\r\n', '\n')+'\n\n'
        super(SBVParser, self).__init__(input_string, pattern, language=language,
             flags=[re.DOTALL], eager_parse=eager_parse)

    def _get_time(self, hour, min, sec, secfr):
        if secfr is None:
            secfr = '0'
        res = (int(hour)*60*60+int(min)*60+int(sec)+float('.'+secfr)) * 1000
        if res >= utils.UNSYNCED_TIME_ONE_HOUR_DIGIT:
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
        text = ('' if match['text'] is None
                else utils.escape_ampersands(match['text']))

        # [br] are linebreaks
        text = text.replace("[br]", "<br/>")

        output['text'] = text

        return output


register(SBVParser)
