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
        super(BaseTextParser, self).__init__(input_string, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.input_string = self.input_string.replace('\r\n', '\n')+u'\n\n'
        self.language = language

register(SBVParser)
