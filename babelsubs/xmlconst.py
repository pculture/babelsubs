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

"""babelsubs.xmlconst -- XML constants """

# XML namespace URIs
TTML_NAMESPACE_URI = 'http://www.w3.org/ns/ttml'
TTML_NAMESPACE_URI_LEGACY = 'http://www.w3.org/2006/04/ttaf1'
TTS_NAMESPACE_URI = 'http://www.w3.org/ns/ttml#styling'
TTM_NAMESPACE_URI = 'http://www.w3.org/ns/ttml#metadata'
XML_NAMESPACE_URI = 'http://www.w3.org/XML/1998/namespace'

# These strings help construct etree tag/attribute names
TTML = '{%s}' % TTML_NAMESPACE_URI
TTM = '{%s}' % TTM_NAMESPACE_URI
TTS = '{%s}' % TTS_NAMESPACE_URI
XML = '{%s}' % XML_NAMESPACE_URI


