from cgi import escape
from babelsubs.generators.base import BaseGenerator, register
import json


class JSONGenerator(BaseGenerator):
    """
    This is just a basic shim around our internal storage which is already in JSON.
    """
    file_type = 'json'

    def __unicode__(self):
        return json.dumps(self.subtitle_set.subtitles)


register(JSONGenerator)
