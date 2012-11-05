"""
General helpers needed by the other tests.
"""

import os

import babelsubs

def get_data_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), 'data', file_name)

def get_subs(file_name):
    return babelsubs.load_from_file(get_data_file_path(file_name))
