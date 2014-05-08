# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org

# Copyright (c) 2012, Participatory Culture Foundation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# - Neither the name of the Participatory Culture Foundation nor the names
# of its contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import babelsubs.parsers as parsers
from babelsubs.parsers.base import ParserList, SubtitleParserError
from babelsubs.generators.base import GeneratorList
import babelsubs.generators as generators

def get_available_formats():
    return sorted(list(set(ParserList.keys()).intersection(set(GeneratorList.keys()))))

def load_from(sub_from, type=None, language=None):
    if hasattr(sub_from, 'read'):
        if type is None and not getattr(sub_from, 'name', None):
            raise TypeError("Couldn't find out the type by myself. Care to specify?")

        extension = sub_from.name.split(".")[-1]
        # if the file extension is not given or is not a registred
        # fallback to the given type
        available_types = get_available_formats()
        target_type = None
        if type and type in available_types:
            target_type = type
        elif extension and extension in available_types:
            target_type = extension
        else: 
            raise TypeError("Type %s is not an available type"  % (type or extension))
        parser = parsers.discover(target_type) 
        with sub_from:
            sub_from = sub_from.read()
    elif isinstance(sub_from, basestring) and type is None:
        raise TypeError("Couldn't find out the type by myself. Care to specify?")
    else:
        parser = parsers.discover(type)

    no_unicode = getattr(parser, 'NO_UNICODE', False)

    if not isinstance(sub_from, unicode):
        if not no_unicode:
            sub_from = sub_from.decode("utf-8")
    else:
        if no_unicode:
            sub_from = sub_from.encode("utf-8")

    return parser.parse(sub_from, language=language)

def load_from_file(filename, type=None, language=None):
    if not os.path.isfile(filename):
        raise ValueError('Invalid filename "%s".' % filename)

    with open(filename) as f:
        return load_from(f, type, language)


def to(subs, type, language=None):
    Generator = generators.discover(type)

    if not Generator:
        raise TypeError("Could not find a type %s" % type)

    return Generator.generate(subs, language=language)

def dfxp_merge(subtitle_sets):
    return generators.DFXPGenerator.merge_subtitles(subtitle_sets)

__all__ = ['load_from', 'load_from_file', 'to', 'get_available_formats',
           'dfxp_merge']
