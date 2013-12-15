from babelsubs.generators.base import BaseGenerator, register


class TXTGenerator(BaseGenerator):
    file_type = 'txt'

    def __init__(self, subtitle_set, line_delimiter=u'\n\n', language=None):
        """
        Generator is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds'}
        """
        self.subtitle_set = subtitle_set
        self.line_delimiter = line_delimiter
        self.language = language

    def __unicode__(self):
        output = []
        for _, _, content, _ in self.subtitle_set.subtitle_items():
            content and output.append(content.strip())

        return self.line_delimiter.join(output)


register(TXTGenerator)

class TXTTranscriptGenerator(BaseGenerator):
    file_type = 'trans'

    def __init__(self, subtitle_set, line_delimiter=u'\n\n', language=None):
        """
        Generator is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds'}
        """
        self.subtitle_set = subtitle_set
        self.line_delimiter = line_delimiter
        self.language = language

    def __unicode__(self):
        output = []
        i = 0
        joined_string = ""
        #Loop to go through all the elements in the subtitle
        for _, _, content, meta in self.subtitle_set.subtitle_items():
            #Skipping first occurrence, because it always start as a new paragraph
            if meta['new_paragraph']:
                if i != 0:
                    joined_string += self.line_delimiter
                    output.append(joined_string)
                    joined_string = ""
                else:
                    #Concatenating strings that belongs to the same paragraph
                    joined_string += " " + content
            else:
                #Concatenating strings that belongs to the same paragraph
                joined_string += " " + content

            #Keeping track of the position
            i += 1
            #If this is the last occurrence, append and leave.
            if i == len(self.subtitle_set.subtitle_items()):
                output.append(joined_string)

        return "".join(output)


register(TXTTranscriptGenerator)