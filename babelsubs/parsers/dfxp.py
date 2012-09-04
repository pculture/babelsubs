from babelsubs import utils
from babelsubs.storage import SubtitleSet
from base import BaseTextParser, SubtitleParserError, register
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

MAX_SUB_TIME = (60 * 60 * 100) - 1

class DFXPParser(BaseTextParser):
    """
    The DFXPParser is in reality just a shim around the basic storage
    mechanism we're using. So most things should be done over storage.py
    """

    file_type = 'dfxp'
    no_unicode = True

    def __init__(self, subtitles, language=None):
        self.subttitle_set = SubtitleSet(language, subtitles, normalize_time=True)

    def __len__(self):
        return self.subttitle_set.__len__()

    def __nonzero__(self):
        return self.subttitle_set.__nonzero__()

    def to_internal(self):
        return self.subttitle_set
        

register(DFXPParser)
