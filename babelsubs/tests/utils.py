"""
General helpers needed by the other tests.
"""

import difflib
import os

import babelsubs

def get_data_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), 'data', file_name)

def get_subs(file_name,language='en'):
    return babelsubs.load_from_file(get_data_file_path(file_name), language=language)

def assert_long_text_equal(text1, text2):
    if text1 != text2:
        diff = difflib.unified_diff(text1.splitlines(True),
                                    text2.splitlines(True),
                                    fromfile="string1",
                                    tofile="string2")
        raise AssertionError("strings differ: %s" % ''.join(diff))
