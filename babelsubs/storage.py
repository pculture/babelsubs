# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

import base64
from lxml import etree
import os
import re
import zlib


SCHEMA_PATH =  os.path.join(os.getcwd(), "data", 'xsdchema', 'all.xsd')
#schema = lxml.etree.XMLSchema(lxml.etree.parse(open(SCHEMA_PATH)))

TIME_EXPRESSION_METRIC = re.compile(r'(?P<num>[\d]{1,})(?P<unit>(h|ms|s|m|f|t))')

def compress(data):
    """Compress a bytestring and return it in a form Django can store.

    If you want to store a Unicode string, you need to encode it to a bytestring
    yourself!

    Django prefers to receive Unicode strings to store in a text field, which
    will mangle normal zip data.  We base64 it to avoid the problem.

    """
    return base64.encodestring(zlib.compress(data))

def decompress(data):
    """Decompress data created with compress."""
    return zlib.decompress(base64.decodestring(data))

def get_attr(el, attr):
    """Get the string of an attribute, or None if it's not present.

    Ignores namespaces to save your sanity.

    """
    for k, v in el.attrib.items():
        if k == attr or k.rsplit('}', 1)[-1] == attr:
            return v

def get_contents(el):
    """Get the contents of the given element as a string of XML.

    Based on
    http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
    but edited to actually work.

    I cannot believe this is not part of lxml.  Seriously, what are they
    thinking?  This is one of the most basic things people would need.

    """
    parts = ([el.text] +
             list(etree.tostring(c) for c in el.getchildren()) +
             [el.tail])
    return ''.join(filter(None, parts)).strip()

def parse_time_expression(time_expression):
    """
    Parses possible values from time expressions[1] to a normalized value
    in milliseconds.

    We don't support all possible forms now, only clock time and metric
    [1] http://www.w3.org/TR/ttaf1-dfxp/#timing-value-timeExpression
    """
    if not time_expression:
        return 0
    # clock-time expression require at lease three parts separated by :
    parts = time_expression.split(":")
    if len(parts) >= 3:
        try:
            hour = int(parts[0])
            minutes = int(parts[1])
            seconds  = int(parts[2])
            milliseconds = 0
            if len(parts) > 3:
                milliseconds = int(float(parts[3]))
            return (((hour * 3600) + (minutes * 60) + seconds ) * 1000 ) + milliseconds
        except ValueError:
            raise ValueError("Time expression %s can't be parsed" % time_expression)
    match = TIME_EXPRESSION_METRIC.match(time_expression)
    if match:
        groups = match.groupdict()
        num, unit = int(groups['num']), groups['unit']
        multiplier = {
            "h": 3600 * 1000,
            "m": 60 * 1000,
            "s": 1000,
            "ms": 1,
            'f': 0,
            't': 0,
        }[unit]
        return num * multiplier

def milliseconds_to_time_clock_components(milliseconds):
    """
    Converts milliseconds (as an int) to the
    hours, minutes, seconds and milliseconds.
    None will be converted to all zeros
    """
    if milliseconds is None:
        return (0,0,0,0) 
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60 )
    hours, minutes = divmod(minutes, 60 )
    return hours, minutes, seconds, milliseconds

def milliseconds_to_time_expression(milliseconds):
    """
    Converts time components to a string suitable to be used on time expression
    fot ttml
    """
    hours, minutes, seconds, milliseconds = milliseconds_to_time_clock_components(milliseconds)
    return '%02d:%02d:%02d:%02d' % (hours, minutes, seconds, milliseconds)


def time_expression_to_millisends(time_expression):
    h,m,s,mil = time_expression.split(":")
    return mil + ((s  + (m * 60) + (h * 3600)) * 1000)

class SubtitleSet(object):
    BASE_TTML = r'''
        <tt xml:lang="%(language_code)s" xmlns="http://www.w3.org/ns/ttml">
            <head>
                <metadata xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
                    <ttm:title>%(title)s</ttm:title>
                    <ttm:description>%(description)s</ttm:description>
                    <ttm:copyright></ttm:copyright>
                </metadata>

                <styling xmlns:tts="http://www.w3.org/ns/ttml#styling">
                    <style xml:id="amara-style"
                        tts:color="white"
                        tts:fontFamily="proportionalSansSerif"
                        tts:fontSize="18px"
                        tts:textAlign="center"
                    />
                </styling>

                <layout xmlns:tts="http://www.w3.org/ns/ttml#styling">
                    <region xml:id="amara-subtitle-area"
                            style="amara-style"
                            tts:extent="560px 62px"
                            tts:padding="5px 3px"
                            tts:backgroundColor="black"
                            tts:displayAlign="after"
                    />
                </layout>
            </head>
            <body region="amara-subtitle-area">
                <div>
                </div>
            </body>
        </tt>
    '''

    SUBTITLE_XML = r'''
        <p xmlns="http://www.w3.org/ns/ttml" %s %s>
            %s
        </p>
    '''

    def __init__(self, language_code, initial_data=None, title=None, description=None):
        """Create a new set of Subtitles, either empty or from a hunk of TTML.

        language_code: The bcp47 code for this language.
        initial_data: any optional xml as the starting point.
        NO UNICODE ALLOWED!  USE XML ENTITIES TO REPRESENT UNICODE CHARACTERS!

        """
        if initial_data:
            self._ttml = etree.fromstring(initial_data % language_code) 
        else:
            self._ttml = etree.fromstring(SubtitleSet.BASE_TTML % {
                'title' : title or '',
                'description': description or '',
                'language_code': language_code or '',
            })


    def __len__(self):
        return len(self.get_subtitles())

    def __iter__(self):
        return self.subtitle_items()

    def get_subtitles(self):
        return self._ttml.xpath('/n:tt/n:body/n:div/n:p',
                                namespaces={'n': 'http://www.w3.org/ns/ttml'})

    def append_subtitle(self, from_ms, to_ms, content):
        """Append a subtitle to the end of the list.

        NO UNICODE ALLOWED!  USE XML ENTITIES TO REPRESENT UNICODE CHARACTERS!

        """
        
        begin = 'begin="%s"' % milliseconds_to_time_expression(from_ms)
        end = 'end="%s"' % milliseconds_to_time_expression(to_ms)

        p = etree.fromstring(SubtitleSet.SUBTITLE_XML % (begin, end, content))
        div = self._ttml.xpath('/n:tt/n:body/n:div',
                               namespaces={'n': 'http://www.w3.org/ns/ttml'})[0]
        div.append(p)

    def subtitle_items(self, allow_format_tags=False):
        """A generator over the subs, yielding (from_ms, to_ms, content) tuples.

        The from and to millisecond values may be any time expression
        that we can parse.
        """
        for el in self.get_subtitles():
            begin = get_attr(el, 'begin')
            end = get_attr(el, 'end')

            from_ms = (parse_time_expression(begin)
                     if begin else None)
            to_ms = (parse_time_expression(end)
                       if end else None)
            if not allow_format_tags:
                content = get_contents(el)
            else:
                raise NotImplementedError("Formatting not supported just yet.")

            yield (from_ms, to_ms, content)


    @classmethod
    def from_blob(cls, blob_data):
        """Return a SubtitleSet from a blob of base64'ed zip data."""
        return SubtitleSet(decompress(blob_data))

    @classmethod
    def from_list(cls, subtitles):
        """Return a SubtitleSet from a list of subtitle tuples.

        Each tuple should be (from_ms, to_ms, content).  See the docstring of
        append_subtitle for more information.

        For example:

            [(0, 1000, "Hello, "),
             (1100, None, "world!")]

        """
        subs = SubtitleSet()

        for s in subtitles:
            subs.append_subtitle(*s)

        return subs


    def to_blob(self):
        return compress(self.to_xml())

    def to_xml(self):
        """Return a string containing the XML for this set of subtitles."""
        return etree.tostring(self._ttml, pretty_print=True)


    def __eq__(self, other):
        if type(self) == type(other):
            return self.to_xml() == other.to_xml()
        else:
            return False


    def validate(self):
        raise NotImplementedError("Validation isnt working so far")
        schema.assertValid(self._ttml)
        
