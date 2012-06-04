# -*- coding: utf-8 -*-

###########################################################################
#    SeriesFinale
#    Copyright (C) 2009 Joaquim Rocha <jrocha@igalia.com>
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

import os
import sys
import gtk

SF_NAME = 'SeriesFinale'
SF_COMPACT_NAME = 'seriesfinale'
SF_VERSION = '0.6.10'
SF_DESCRIPTION = 'SeriesFinale is a TV series browser and tracker application'
SF_URL = 'http://www.igalia.com'
SF_COPYRIGHT = 'Copyright © 2010-2011 Igalia S. L.'
SF_AUTHORS = ['Joaquim Rocha <jrocha@igalia.com>',
              'Juan A. Suarez <jasuarez@igalia.com>']
SF_LICENSE = \
"""%(sf_name)s is free software: you can redistribute it and/or modify \
it under the terms of the GNU General Public License as published by \
the Free Software Foundation, either version 3 of the License, or \
(at your option) any later version.

%(sf_name)s is distributed in the hope that it will be useful, \
but WITHOUT ANY WARRANTY; without even the implied warranty of \
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the \
GNU General Public License for more details.

You should have received a copy of the GNU General Public License \
along with %(sf_name)s.  If not, see <http://www.gnu.org/licenses/>.
""" % {'sf_name': SF_NAME}

HOME_PATH = os.getenv('HOME')
SF_CONF_FOLDER = HOME_PATH + '/.osso/%s' % SF_COMPACT_NAME
SF_CONF_FILE = SF_CONF_FOLDER + '/%s.conf' % SF_COMPACT_NAME
SF_DB_FILE = SF_CONF_FOLDER + '/%s' % 'series.db'
SF_PID_FILE = '/tmp/seriesfinale.pid'
SF_LANG_FILE = SF_CONF_FOLDER + '/%s' % 'languages.db'
_XDG_DATA_HOME = os.getenv('XDG_DATA_HOME') or ''
_XDG_DATA_HOME = _XDG_DATA_HOME.split(':')[0]
_DATA_DIR_PREFIX = _XDG_DATA_HOME or os.path.join(HOME_PATH, '.local', 'share')
DATA_DIR = os.path.join(_DATA_DIR_PREFIX, SF_COMPACT_NAME)
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
    except:
        print 'Error trying to make: ', DATA_DIR

DEFAULT_SYSTEM_APP_DIR = os.path.join(sys.prefix,
                                      'share',
                                      SF_COMPACT_NAME)
APP_DIR = DEFAULT_SYSTEM_APP_DIR

if not os.path.exists(APP_DIR):
    APP_DIR = os.path.dirname(os.path.dirname(__file__))
    APP_DIR = os.path.join(APP_DIR, 'data')

PLACEHOLDER_IMAGE = os.path.join(APP_DIR, 'placeholderimage.png')
DOWNLOADING_IMAGE = os.path.join(APP_DIR, 'downloadingimage.png')

LOCALE_DIR = os.path.join(APP_DIR, 'locale')


DEFAULT_LANGUAGES = os.environ.get('LANGUAGE', '').split(':')
DEFAULT_LANGUAGES += ['en_US', 'pt_PT']

ICON_FOLDER = 'share/icons/hicolor/scalable/apps'
SF_ICON = os.path.join(sys.prefix, ICON_FOLDER, SF_COMPACT_NAME + '.png')

TVDB_API_KEY = 'FAD75AF31E1B1577'

SECONDARY_TEXT_COLOR = 'SecondaryTextColor'
ACTIVE_TEXT_COLOR = 'ActiveTextColor'

IMAGE_WIDTH = 100
IMAGE_HEIGHT = 60

SAVE_TIMEOUT_MS = 300000

