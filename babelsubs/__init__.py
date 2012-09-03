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

    if not isinstance(sub_from, unicode):
        sub_from = sub_from.decode("utf-8")

    return parsers.discover(type).parse(sub_from, language=language)

__all__ = ['load_from']
