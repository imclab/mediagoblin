# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011 Free Software Foundation, Inc
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

from mediagoblin.gmg_commands import util as commands_util
from mediagoblin import mg_globals
from mediagoblin.db import util as db_util
from mediagoblin.db.open import setup_connection_and_db_from_config
from mediagoblin.init.config import read_mediagoblin_config

import shlex
import tarfile
import subprocess
import os.path

def import_export_parse_setup(subparser):
    # TODO: Add default
    subparser.add_argument(
        'tar_file')
    subparser.add_argument(
        '-cf', '--conf_file', default='mediagoblin.ini',
        help='Config file used to set up environment')
    subparser.add_argument(
        '--mongodump_cache', default='mongodump',
        help='mongodump cache directory')
    subparser.add_argument(
        '--mongodump_path', default='mongodump',
        help='mongodump binary')

def _export_database(db, args):
    print "\n== Exporting database ==\n"

    command = '{mongodump_path} -d {database} -o {mongodump_cache}'.format(
        mongodump_path=args.mongodump_path,
        database=db.name,
        mongodump_cache=args.mongodump_cache)
    
    p = subprocess.Popen(
        shlex.split(command))
    
    p.wait()

    print "\n== Database exported ==\n"

def _import_database(db, args):
    pass

def env_import(args):    
    config, validation_result = read_mediagoblin_config(args.conf_file)
    connection, db = setup_connection_and_db_from_config(
        config['mediagoblin'], use_pymongo=True)

def env_export(args):
    config, validation_result = read_mediagoblin_config(args.conf_file)
    connection, db = setup_connection_and_db_from_config(
        config['mediagoblin'], use_pymongo=True)

    if os.path.exists(args.tar_file):
        overwrite = raw_input(
            'The output file already exists. '
            'Are you **SURE** you want to overwrite it? '
            '(yes/no)> ')
        if not overwrite == 'yes':
            print "Aborting."
            return

    tf = tarfile.open(
        args.tar_file,
        mode='w|gz')


    _export_database(db, args)
    
    tf.add(args.mongodump_cache)
    
