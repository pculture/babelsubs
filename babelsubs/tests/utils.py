"""
General helpers needed by the other tests.
"""

import os

from babelsubs import parsers

def get_data_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), 'data', file_name)

def get_subs(file_name):
    data = open(get_data_file_path(file_name)).read()
    extension = os.path.splitext(file_name)[1][1:]
    return parsers.discover(extension).parse(data)
