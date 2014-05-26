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

"""babelsubs.loader -- create subtitle sets."""

import os.path

from lxml import etree

from babelsubs import parsers
from babelsubs import storage
from babelsubs.generators.dfxp import DFXPGenerator
from babelsubs.xmlconst import *

class SubtitleLoader(object):
    """SubtitleLoader -- Create SubtitleSets

    SubtitleLoader provides a way to creating SubtitleSet objects with custom
    layout/styling sections.  It supports both creating new subtitles and
    parsing them from other formats.
    """

    def __init__(self):
        self.styles = []
        self.regions = []

    def add_style(self, xml_id, **attrib):
        """Add a custom style to the created SubtitleSets.

        Each add_style() call will create a new style element in the TTML.  At
        least one style must be added before creating subtitles.

        :param xml_id: xml:id attribute to use
        :param attribs: extra attributes to set.  Each attribute name will
        have the TTS namespace prefixed to it.
        """
        self.styles.append((xml_id, attrib))

    def add_region(self, xml_id, style_id, **attrib):
        """Add a custom region to the created SubtitleSets.

        Each add_region() call will create a new region element in the TTML.  At
        least one region must be added before creating subtitles.

        The first region added will be the default region for the body.

        :param xml_id: xml:id attribute to use
        :param style_id: style to use for this region
        :param attribs: extra attributes to set.  Each attribute name will
        have the TTS namespace prefixed to it.
        """
        self.regions.append((xml_id, style_id, attrib))

    def _empty_ttml(self, language_code, title, description):
        if not self.styles:
            raise ValueError("no styles added")
        if not self.regions:
            raise ValueError("no regions added")

        tt = etree.Element(TTML + 'tt', attrib={
            XML + 'lang': language_code,
        }, nsmap = {
            None: TTML_NAMESPACE_URI,
            'tts': TTS_NAMESPACE_URI,
            'ttm': TTM_NAMESPACE_URI,
        })
        head = etree.SubElement(tt, TTML + 'head')
        head.append(self._create_metadata(title, description))
        head.append(self._create_styling())
        head.append(self._create_layout())
        tt.append(self._create_empty_body())
        return tt

    def _create_metadata(self, title, description):
        metadata = etree.Element(TTML + 'metadata')
        etree.SubElement(metadata, TTM + 'title').text = title
        etree.SubElement(metadata, TTM + 'description').text = description
        etree.SubElement(metadata, TTM + 'copyright')
        return metadata

    def _create_styling(self):
        styling = etree.Element(TTML + 'styling')
        for (xml_id, attrib) in self.styles:
            style = etree.SubElement(styling, TTML + 'style')
            style.set(XML + 'id', xml_id)
            for name, value in attrib.items():
                style.set(TTS + name, value)
        return styling

    def _create_layout(self):
        layout = etree.Element(TTML + 'layout')
        for (xml_id, style_id, attrib) in self.regions:
            region = etree.SubElement(layout, TTML + 'region')
            region.set(XML + 'id', xml_id)
            region.set(TTML + 'style', style_id)
            for name, value in attrib.items():
                region.set(TTS + name, value)
        return layout

    def _create_empty_body(self):
        body = etree.Element(TTML + 'body', attrib={
            TTML + 'region': self.regions[0][0],
        })
        return body

    def create_new(self, language_code, title='', description=''):
        """Create a new SubtitleSet.  """
        ttml = self._empty_ttml(language_code, title, description)
        # add an empty div to start the subtitles
        etree.SubElement(ttml.find(TTML + 'body'), TTML + 'div')
        return storage.SubtitleSet.create_with_raw_ttml(ttml)

    def dfxp_merge(self, subtitle_sets):
        """Create a merged DFXP file from a list of subtitle sets."""
        initial_ttml = self._empty_ttml('', '', '')
        return DFXPGenerator.merge_subtitles(subtitle_sets, initial_ttml)

    def load(self, language_code, path):
        """Create a SubtitleSet with existing subtitles.

        If path is a DFXP file, then we will simply load it and return.  If
        it has any other format, we will create a DFXP template using our
        styles/regions and load the subtitles into that.  The reason for this
        is that if we are reading DFXP we don't want to ovewrite the styles
        inside the file with our own.
        """

        basename, ext = os.path.splitext(path)
        with open(path) as f:
            content = f.read()

        return self.loads(language_code, content, ext[1:].lower())

    def loads(self, language_code, content, file_type):
        try:
            parser = parsers.discover(file_type)
        except KeyError:
            raise TypeError("No parser for %s" % file_type)


        parsed_subs = parser.parse(content,
                                   language=language_code).to_internal()
        if parser is parsers.DFXPParser:
            # return the subtitles as-is
            return parsed_subs

        ttml  = self._empty_ttml(language_code, '', '')
        self._move_elements(parsed_subs._ttml.find(TTML + 'body'),
                            ttml.find(TTML + 'body'))
        return storage.SubtitleSet.create_with_raw_ttml(ttml)

    def _remove_intial_div(self, subtitle_set):
        body = subtitle_set._ttml.find(TTML + 'body')
        body.remove(body[0])

    def _move_elements(self, source, dest):
        """Move children from one etree element to another."""
        children = list(source)
        source.clear()
        for child in children:
            dest.append(child)
