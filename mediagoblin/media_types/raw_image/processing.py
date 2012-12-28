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

import Image
import os
import logging

from mediagoblin import mg_globals as mgg
from mediagoblin.processing import create_pub_filepath, FilenameBuilder
from mediagoblin.media_types.image.processing import resize_image
from mediagoblin.tools.exif import extract_exif, \
    clean_exif, get_gps_data, exif_image_needs_rotation

_log = logging.getLogger(__name__)


SUPPORTED_FILETYPES = ['nef']

# The entire function have to be copied

def sniff_handler(media_file, **kw):
    if kw.get('media') is not None:  # That's a double negative!
        name, ext = os.path.splitext(kw['media'].filename)
        clean_ext = ext[1:].lower()  # Strip the . from ext and make lowercase

        if clean_ext in SUPPORTED_FILETYPES:
            _log.info('Found file extension in supported filetypes')
            return True
        else:
            _log.debug('Media present, extension not found in {0}'.format(
                    SUPPORTED_FILETYPES))
    else:
        _log.warning('Need additional information (keyword argument \'media\')'
                     ' to be able to handle sniffing')

    return False


def process_image(entry):
    """
    Code to process an image
    """
    workbench = mgg.workbench_manager.create_workbench()
    # Conversions subdirectory to avoid collisions
    conversions_subdir = os.path.join(
        workbench.dir, 'conversions')
    os.mkdir(conversions_subdir)
    queued_filepath = entry.queued_media_file
    queued_filename = workbench.localized_file(
        mgg.queue_store, queued_filepath,
        'source')
    name_builder = FilenameBuilder(queued_filename)

    # EXIF extraction
    exif_tags = extract_exif(queued_filename)
    gps_data = get_gps_data(exif_tags)

    # This is the only special raw/NEF code

    import pyexiv2
    # Read EXIF data
    md = pyexiv2.ImageMetadata(queued_filename)
    md.read()
    tmp_resized_filename = os.path.join(conversions_subdir,
        queued_filepath[-1])

    # Extract the biggest preview and write it as our working image
    md.previews[-1].write_to_file(tmp_resized_filename.encode('utf-8'))


    # Always create a small thumbnail
    thumb_filepath = create_pub_filepath(
        entry, name_builder.fill('{basename}.thumbnail{ext}'))
    resize_image(entry, queued_filename, thumb_filepath,
                exif_tags, conversions_subdir,
                (mgg.global_config['media:thumb']['max_width'],
                 mgg.global_config['media:thumb']['max_height']))

    # If the size of the original file exceeds the specified size of a `medium`
    # file, a `.medium.jpg` files is created and later associated with the media
    # entry.
    medium = Image.open(queued_filename)
    if medium.size[0] > mgg.global_config['media:medium']['max_width'] \
        or medium.size[1] > mgg.global_config['media:medium']['max_height'] \
        or exif_image_needs_rotation(exif_tags):
        medium_filepath = create_pub_filepath(
            entry, name_builder.fill('{basename}.medium{ext}'))
        resize_image(
            entry, queued_filename, medium_filepath,
            exif_tags, conversions_subdir,
            (mgg.global_config['media:medium']['max_width'],
             mgg.global_config['media:medium']['max_height']))
    else:
        medium_filepath = None

    # we have to re-read because unlike PIL, not everything reads
    # things in string representation :)
    queued_file = file(queued_filename, 'rb')

    with queued_file:
        original_filepath = create_pub_filepath(
            entry, name_builder.fill('{basename}{ext}'))

        with mgg.public_store.get_file(original_filepath, 'wb') \
            as original_file:
            original_file.write(queued_file.read())

    # Remove queued media file from storage and database
    mgg.queue_store.delete_file(queued_filepath)
    entry.queued_media_file = []

    # Insert media file information into database
    media_files_dict = entry.setdefault('media_files', {})
    media_files_dict[u'thumb'] = thumb_filepath
    media_files_dict[u'original'] = original_filepath
    if medium_filepath:
        media_files_dict[u'medium'] = medium_filepath

    # Insert exif data into database
    exif_all = clean_exif(exif_tags)

    if len(exif_all):
        entry.media_data_init(exif_all=exif_all)

    if len(gps_data):
        for key in list(gps_data.keys()):
            gps_data['gps_' + key] = gps_data.pop(key)
        entry.media_data_init(**gps_data)

    # clean up workbench
    workbench.destroy_self()
