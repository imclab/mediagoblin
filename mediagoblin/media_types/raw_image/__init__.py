# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging

from mediagoblin.media_types.image import ImageMediaManager
from mediagoblin.tools import pluginapi

from .processing import sniff_handler, RawImageProcessingManager

_log = logging.getLogger(__name__)


ACCEPTED_EXTENSIONS = ["nef", "cr2"]
MEDIA_TYPE = 'mediagoblin.media_types.raw_image'


def setup_plugin():
    pluginapi.get_config(MEDIA_TYPE)


class RawImageMediaManager(ImageMediaManager):
    human_readable = "Raw image"
    #display_template = "mediagoblin/media_displays/image.html"
    #default_thumb = "images/media_thumbs/image.png"

    #media_fetch_order = [u'medium', u'original', u'thumb']


def get_media_type_and_manager(ext):
    _log.debug('getmediatype: '+ ext)
    if ext.lower() in ACCEPTED_EXTENSIONS:
        return MEDIA_TYPE, RawImageMediaManager
    _log.debug('getmediatype NOFOUND!')


hooks = {
    'setup': setup_plugin,
    'get_media_type_and_manager': get_media_type_and_manager,
    'sniff_handler': sniff_handler,
    ('media_manager', MEDIA_TYPE): lambda: RawImageMediaManager,
    ('reprocess_manager', MEDIA_TYPE): lambda: RawImageProcessingManager,
}
