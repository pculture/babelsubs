import re

from babelsubs.parsers.srt import SRTParser
from babelsubs.utils import (
    centiseconds_to_milliseconds, escape_ampersands,
    UNSYNCED_TIME_ONE_HOUR_DIGIT
)
from base import register

class SSAParser(SRTParser):

    file_type = ['ssa', 'ass']
    MAX_SUB_TIME = UNSYNCED_TIME_ONE_HOUR_DIGIT

    def __init__(self, input_string, language=None, eager_parse=True):
        pattern = r'Dialogue: [\w=]+,' #Dialogue: <Marked> or <Layer>,
        pattern += r'(?P<s_hour>\d):(?P<s_min>\d{2}):(?P<s_sec>\d{2})[\.\:](?P<s_secfr>\d+),' #<Start>,
        pattern += r'(?P<e_hour>\d):(?P<e_min>\d{2}):(?P<e_sec>\d{2})[\.\:](?P<e_secfr>\d+),' #<End>,
        pattern += r'[\w ]+,' #<Style>,
        pattern += r'[\w ]*,' #<Character name>,
        pattern += r'\d{4},\d{4},\d{4},' #<MarginL>,<MarginR>,<MarginV>,
        pattern += r'[\w ]*,' #<Efect>,
        pattern += r'(?:\{.*?\})?(?P<text>.+?)\n' #[{<Override control codes>}]<Text>
        #replace \r\n to \n and fix end of last subtitle
        input_string = input_string.replace('\r\n', '\n')+'\n'
        self.markup_re = re.compile(r"{\\(?P<start>[biu])1}(?P<text>.+?){\\(?P<end>[biu])0}")
        super(SRTParser, self).__init__(input_string, pattern, flags=[re.DOTALL],
            language=language, eager_parse=eager_parse)

    def get_markup(self, text):
        return self.markup_re.sub(self.__replace, text)
    
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
        output['text'] = ('' if match['text'] is None else
                          escape_ampersands(match['text']))

        return output

    def _get_time(self, hour, min, sec, milliseconds):
        milliseconds = centiseconds_to_milliseconds(milliseconds)
        res =  (1000 * (
            (int(hour)*60*60 )+
            (int(min)*60) +
            int(sec))) + milliseconds
        if res >= self.MAX_SUB_TIME:
            return None
        return res

    def __replace(self, match):
        group = match.groupdict()
        if group['start'] != group['end']:
            raise ValueError("Unbalanced tags start: %(start)s, end: %(end)s" % group)

        base_span = '<span %s>%s</span>'

        if group['start'] == 'b':
            span = base_span % ('fontWeight="bold"', group['text'])
        elif group['start'] == 'i':
            span = base_span % ('fontStyle="italic"', group['text'])
        elif group['start'] == 'u':
            span = base_span % ('textDecoration="underline"', group['text'])

        return span


register(SSAParser)
