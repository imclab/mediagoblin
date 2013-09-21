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

import os
import logging

#from mediagoblin import mg_globals as mgg
from mediagoblin.processing import (
    ProcessingManager)

from mediagoblin.media_types.image.processing import (
    InitialProcessor, Resizer)

_log = logging.getLogger(__name__)


MEDIA_TYPE = 'mediagoblin.media_types.raw_image'
SUPPORTED_FILETYPES = ['nef']

# The entire function have to be copied

def sniff_handler(media_file, **kw):
    _log.info('Sniffing {0}'.format(MEDIA_TYPE))
    if kw.get('media') is not None:  # That's a double negative!
        name, ext = os.path.splitext(kw['media'].filename)
        clean_ext = ext[1:].lower()  # Strip the . from ext and make lowercase

        if clean_ext in SUPPORTED_FILETYPES:
            _log.info('Found file extension in supported filetypes')
            return MEDIA_TYPE
        else:
            _log.debug('Media present, extension not found in {0}'.format(
                    SUPPORTED_FILETYPES))
    else:
        _log.warning('Need additional information (keyword argument \'media\')'
                     ' to be able to handle sniffing')

    return None


class InitialRawProcessor(InitialProcessor):
    def common_setup(self):
        """
        Set up the workbench directory and pull down the original file
        """
        super(self.__class__, self).common_setup()
        self._original_raw = self.process_filename
        import pyexiv2
        # Read EXIF data
        md = pyexiv2.ImageMetadata(self._original_raw)
        md.read()
        self.process_filename = os.path.join(self.conversions_subdir,
            self.entry.queued_media_file[-1])

        # Extract the biggest preview and write it as our working image
        md.previews[-1].write_to_file(self.process_filename.encode('utf-8'))
        _log.debug('Wrote new file from {0} to preview (jpg) {1}'.format(
            self._original_raw, self.process_filename))



class RawImageProcessingManager(ProcessingManager):
    def __init__(self):
        _log.debug('RawImageProcessingManager')
        super(self.__class__, self).__init__()
        self.add_processor(InitialRawProcessor)
        self.add_processor(Resizer)

#    # This is the only special raw/NEF code
#
#    import pyexiv2
#    # Read EXIF data
#    md = pyexiv2.ImageMetadata(queued_filename)
#    md.read()
#    tmp_resized_filename = os.path.join(conversions_subdir,
#        queued_filepath[-1])
#
#    # Extract the biggest preview and write it as our working image
#    md.previews[-1].write_to_file(tmp_resized_filename.encode('utf-8'))



