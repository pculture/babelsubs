from babelsubs.utils import UNSYNCED_TIME_FULL

class BaseGenerator(object):
    file_type = ''
    allows_formatting = False

    UNSYNCED_TIME = UNSYNCED_TIME_FULL
    def __init__(self, subtitle_set, line_delimiter=u'\n', language=None):
        """
        Generator is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds'}
        """
        self.subtitle_set = subtitle_set
        self.line_delimiter = line_delimiter
        self.language = language

    def __unicode__(self):
        raise Exception('Should return subtitles')

    @classmethod
    def isnumber(cls, val):
        return isinstance(val, (int, long, float))

    @classmethod
    def generate(cls, subtitle_set, language=None):
        return unicode(cls(subtitle_set, language=language))

class GeneratorListClass(dict):

    def register(self, handler, type=None):
        file_type = handler.file_type

        if isinstance(file_type, list):
            for ft in file_type:
                self[ft.lower()] = handler
        else:
            self[file_type] = handler

    def __getitem__(self, item):
        return super(GeneratorListClass, self).__getitem__(item.lower())

GeneratorList = GeneratorListClass()

def register(generator):
    GeneratorList.register(generator)

def discover(type):
    return GeneratorList[type]
