import re

from babelsubs.parsers.srt import SRTParser
from base import register

class SSAParser(SRTParser):

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
        super(SRTParser, self).__init__(file, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.input_string = self.input_string.replace('\r\n', '\n')+u'\n'
        self.language = language
        self.markup_re = re.compile(r"{\\(?P<start>[biu])1}(?P<text>.+?){\\(?P<end>[biu])0}")

    def get_markup(self, text):
        return self.markup_re.sub(self.__replace, text)
    
    def _get_data(self, match):
        r = match.groupdict()
        output = {}
        output['start'] = self._get_time(r['s_hour'], r['s_min'], r['s_sec'], r['s_secfr'])
        output['end'] = self._get_time(r['e_hour'], r['e_min'], r['e_sec'], r['e_secfr'])
        output['text'] = '' if r['text'] is None else r['text']

        return output

    def _get_time(self, hour, min, sec, secfr):
        if secfr is None:
            secfr = '0'

        hour, min, sec, fr = int(hour) * 3600, int(min) * 60, int(sec), float('.'+secfr)/10
        return (hour + min + sec + fr) * 1000

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
