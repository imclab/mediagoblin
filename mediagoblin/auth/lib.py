# GNU Mediagoblin -- federated, autonomous media hosting
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

import os

import bcrypt


def bcrypt_check_password(raw_pass, stored_hash, extra_salt=None):
    """
    Check to see if this password matches.

    Args:
    - raw_pass: user submitted password to check for authenticity.
    - stored_hash: The hash of the raw password (and possibly extra
      salt) to check against
    - extra_salt: (optional) If this password is with stored with a
      non-database extra salt (probably in the config file) for extra
      security, factor this into the check.

    Returns:
      True or False depending on success.
    """
    if extra_salt:
        raw_pass = u"%s:%s" % (extra_salt, raw_pass)

    hashed_pass = bcrypt.hashpw(raw_pass, stored_hash)

    # Reduce risk of timing attacks by hashing again with a random
    # number (thx to zooko on this advice, which I hopefully
    # incorporated right.)
    #
    # See also: 
    rand_salt = bcrypt.gensalt(5)
    randplus_stored_hash = bcrypt.hashpw(stored_hash, rand_salt)
    randplus_hashed_pass = bcrypt.hashpw(hashed_pass, rand_salt)

    return randplus_stored_hash == randplus_hashed_pass


def bcrypt_gen_password_hash(raw_pass, extra_salt=None):
    """
    Generate a salt for this new password.

    Args:
    - raw_pass: user submitted password
    - extra_salt: (optional) If this password is with stored with a
      non-database extra salt
    """
    if extra_salt:
        raw_pass = u"%s:%s" % (extra_salt, raw_pass)

    return bcrypt.hashpw(raw_pass, bcrypt.gensalt())
