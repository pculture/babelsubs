import os

from babelsubs import parsers
from babelsubs.storage import SubtitleSet

class SubtitleLoader(object):
    """SubtitleLoader -- Create SubtitleSets"""

    def create_new(self, language_code, title='', description='',
                   frame_rate=None, frame_rate_multiplier=None, drop_mode=None):
        # TODO: figure out what to do with frame_rate, multiplier, and drop mode since they
        #       aren't referenced anywhere but ITT generation
        return SubtitleSet(language_code, title=title, description=description)

    def load(self, language_code, path):
        """Create a SubtitleSet with existing subtitles."""
        basename, ext = os.path.splitext(path)
        with open(path) as f:
            content = f.read()

        return self.loads(language_code, content, ext[1:].lower())

    def loads(self, language_code, content, file_type):
        try:
            parser = parsers.discover(file_type)
        except KeyError:
            raise TypeError("No parser for {}".format(file_type))

        parsed_subs = parser.parse(content, language=language_code).to_internal()
        return parsed_subs
