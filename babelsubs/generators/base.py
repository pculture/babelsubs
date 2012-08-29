class BaseGenerator(object):
    file_type = ''
    allows_formatting = False

    def __init__(self, subtitles, line_delimiter=u'\n', language=None):
        """
        Generator is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds'}
        """
        self.subtitles = subtitles
        self.line_delimiter = line_delimiter
        self.language = language

    def __unicode__(self):
        raise Exception('Should return subtitles')

    @classmethod
    def isnumber(cls, val):
        return isinstance(val, (int, long, float))

    @classmethod
    def generate(cls, subtitles, language=None):
        return unicode(cls(subtitles=subtitles, language=language))

class GeneratorListClass(dict):

    def register(self, handler, type=None):
        self[type or handler.file_type] = handler

    def __getitem__(self, item):
        return self.get(item, None)

GeneratorList = GeneratorListClass()

def register(generator):
    GeneratorList.register(generator)

def discover(type):
    return GeneratorList[type]
