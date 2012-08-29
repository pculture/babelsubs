import os
import parsers

def load_from(sub_from, type=None, language=None):
    if os.path.isfile(sub_from):
        sub_from = open(sub_from)

    if hasattr(sub_from, 'read'):
        if type is None and not getattr(sub_from, 'name', None):
            raise TypeError("Couldn't find out the type by myself. Care to specify?")

        type = sub_from.name.split(".")[-1]

        with sub_from:
            sub_from = sub_from.read()
    elif isinstance(sub_from, basestring) and type is None:
        raise TypeError("Couldn't find out the type by myself. Care to specify?")

    return parsers.discover(type).parse(sub_from, language=language)

__all__ = ['load_from']
