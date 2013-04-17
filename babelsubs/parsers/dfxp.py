from babelsubs.storage import SubtitleSet
from base import BaseTextParser, SubtitleParserError, register
from xml.parsers.expat import ExpatError
from lxml.etree import XMLSyntaxError

MAX_SUB_TIME = (60 * 60 * 100) - 1

class DFXPParser(BaseTextParser):
    """
    The DFXPParser is in reality just a shim around the basic storage
    mechanism we're using. So most things should be done over storage.py
    """

    file_type = ['dfxp', 'xml']
    NO_UNICODE = True

    def __init__(self, input_string, language=None):
        try:
            self.subtitle_set = SubtitleSet(language, input_string, normalize_time=True)
        except (XMLSyntaxError, ExpatError), e:
            raise SubtitleParserError("There was an error while we were parsing your xml", e)

        self.language = language

    def __len__(self):
        return self.subtitle_set.__len__()

    def __nonzero__(self):
        return self.subtitle_set.__nonzero__()

    def to_internal(self):
        return self.subtitle_set
        

register(DFXPParser)
