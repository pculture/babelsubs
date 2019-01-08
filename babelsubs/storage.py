import os
import unicodedata
import utils

from collections import namedtuple

# TODO: decide whether or not to move Differ to a new module
import difflib
from itertools import izip_longest, izip

SubtitleLine = namedtuple("SubtitleLine", ['start_time', 'end_time', 'text',
                                           'new_paragraph', 'region', 'meta'])

# Example JSON SubtitleSet format:
# {
#   'title': 'Example Subtitles',
#   'language_code': 'en',
#   'description': 'This is an example of a SubtitleSet in JSON.',
#   'metadata': '',
#   'subtitles': [
#      {'start_time': '0',
#       'end_time': '1',
#       'text': 'example text',
#       'new_paragraph': false,
#       'region': 'top',
#       'meta': ''},
#      {'start_time': '1',
#       'end_time': '2',
#       'text': 'more example text',
#       'new_paragraph': false,
#       'region': 'bottom',
#       'meta': ''},
#   ],
# }
class SubtitleSet(object):
    """Internal representation of subtitles in JSON."""

    def __init__(self, language_code, title=None, description=None,
                 metadata=None):
        """Create a new set of subtitles.

        language_code: The bcp47 code for this language.
        metadata: Any style or other metadata to be preserved when re-exporting.
        """
        self.language_code = language_code
        self.title = title
        self.description = description
        self.metadata = metadata
        self.subtitles = []
        # NOTE: get_subtitles() is just self.subtitles
        # NOTE: subtitle_items() is also just self.subtitles
        # NOTE: get_language() and set_language() are now accessed by self.language_code
        # NOTE: parsers are responsible for building SubtitleSets with append_subtitle
        #       instead of creating via raw ttml
        # NOTE: parsers are responsible for converting time into milliseconds

    def __len__(self):
        return len(self.subtitles)

    def __getitem__(self, key):
        return self.subtitles[key]  # should we catch exceptions here or let them fall through?

    def __eq__(self, other):
        if type(self) == type(other):
            return not diff(self, other)['changed']
        else:
            return False

    def __nonzero__(self):
        return bool(self.__len__())

    def append_subtitle(self, start, end, content, new_paragraph=False,
                        region=None, meta=None):
        """Append a subtitle to the end of the list."""
        # remove control characters
        content = filter(lambda c: unicodedata.category(c)[0] != 'C', unicode(content))
        content = utils.strip_tags(content)
        content = utils.unescape_html(content)
        # make sure unsynced subtitles don't break on conversion, but make sure we can preserve 0
        start = float(start) if start is not None else None
        end = float(end) if end is not None else None
        subtitle = SubtitleLine(start_time=start, end_time=end, text=content,
                                new_paragraph=new_paragraph, region=region, meta=meta)
        self.subtitles.append(subtitle)     # can namedtuples() be converted into json easily?

    def subtitle_is_synced(self, subtitle):
        """Checks if a given subtitle has non-empty start and end times,
           and checks that the end is after the start."""
        start, end = getattr(subtitle, 'start_time', None), getattr(subtitle, 'end_time', None)
        # allow 0 as an initial start value
        if (start is not None and end is not None) and end > start:
            return True
        return False

    @property
    def fully_synced(self):
        for subtitle in self.subtitles:
            if not self.subtitle_is_synced(subtitle):
                return False
        return True

    @classmethod
    def from_list(cls, language_code, subtitles):
        # TODO: remove "escape" kwarg from from_list() calls
        """Return a SubtitleSet from a list of subtitle tuples.

        Each tuple should be (start_ms, end_ms, content(, optional_kwargs)).

        Example:
            [(0, 100, "Hello, ", {'new_paragraph':True}), (1100, None, "world!")]
        """
        subtitle_set = SubtitleSet(language_code=language_code)

        for subtitle in subtitles:
            extra = {}
            if len(subtitle) > 3:
                extra = subtitle[3]
                subtitle = subtitle[:-1]
            subtitle_set.append_subtitle(*subtitle, **extra)
        return subtitle_set


class _Differ(object):
    def __init__(self, set1, set2):
        self.items1 = set1.subtitles
        self.items2 = set2.subtitles

    def _subtitles_sequence(self, subtitles):
        return [(s.start_time, s.end_time, s.text) for s in subtitles]

    def _time_sequence(self, subtitles):
        return [(s.start_time, s.end_time) for s in subtitles]

    def _text_sequence(self, subtitles):
        return [(s.text,) for s in subtitles]

    def calc_diff(self):
        return {
            'text_changed': self.calc_text_changed(),
            'time_changed': self.calc_time_changed(),
            'changed': self.items1 != self.items2,
            'subtitle_data': self.calc_subtitle_data(),
        }

    # TODO: figure out if we can simplify these to remove messy difflib delta calculations
    def calc_time_changed(self):
        sm = difflib.SequenceMatcher(None,
                self._time_sequence(self.items1), self._time_sequence(self.items2))
        return 1.0 - sm.ratio()

    def calc_text_changed(self):
        sm = difflib.SequenceMatcher(None,
                self._text_sequence(self.items1), self._text_sequence(self.items2))
        return 1.0 - sm.ratio()

    def calc_subtitle_data(self):
        # when calculating, we only match against times/text and ignore metadata
        sm = difflib.SequenceMatcher(None,
                self._subtitles_sequence(self.items1), self._subtitles_sequence(self.items2))
        subtitle_diff = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag is 'equal':
                for i, j in izip(xrange(i1, i2), xrange(j1, j2)):
                    subtitle_diff.append(self.make_subtitle_diff_item(i, j))
            elif tag is 'replace':
                for i, j in izip_longest(xrange(i1, i2), xrange(j1, j2)):
                    subtitle_diff.append(self.make_subtitle_diff_item(i, j))
            elif tag is 'delete':
                for i in xrange(i1, i2):
                    subtitle_diff.append(self.make_subtitle_diff_item(i, None))
            elif tag is 'insert':
                for j in xrange(j1, j2):
                    subtitle_diff.append(self.make_subtitle_diff_item(None, j))
        return subtitle_diff

    def make_subtitle_diff_item(self, i, j):
        if i is not None:
            s1 = self.items1[i]
        else:
            s1 = SubtitleLine(None, None, None, None, None, None)
        if j is not None:
            s2 = self.items2[j]
        else:
            s2 = SubtitleLine(None, None, None, None, None, None)
        return {
            'time_changed': ((s1.start_time, s1.end_time) !=
                             (s2.start_time, s2.end_time)),
            'text_changed': s1.text != s2.text,
            'subtitles': (s1, s2),
        }

def diff(set1, set2):
    """Performs a simple diff, only taking into account:
        - Start and end time
        - Text

    The returned data looks like this: {
        changed: bool,
        text_changed: (float between 0 and 1),
        time_changed: (float between 0 and 1),
        subtitle_data: [
            {
                time_changed: bool,
                text_changed: bool,
                subtitles: [subtitle_line1, subtitle_line2],
            },
        ]}
    """
    return _Differ(set1, set2).calc_diff()

def calc_changes(set1, set2):
    """Returns the time and text changes for two subtitle sets as a tuple."""
    differ = _Differ(set1, set2)
    return differ.calc_text_changed(), differ.calc_time_changed()
