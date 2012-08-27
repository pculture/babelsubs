from babel.generators.ttml import TTMLGenerator
from babel.generators.base import register

class DFXPGenerator(TTMLGenerator):
    file_type = 'dfxp'

    def _get_attributes(self, item):
        attrib = {}
        attrib['begin'] = self.format_time(item['start'])
        attrib['end'] = self.format_time(item['end'])
        return attrib

register(DFXPGenerator)
