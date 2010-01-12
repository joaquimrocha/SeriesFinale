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

SF_NAME = 'SeriesFinale'
SF_COMPACT_NAME = 'seriesfinale'
SF_VERSION = '0.3'
SF_DESCRIPTION = 'SeriesFinale is a TV series browser and tracker application'
SF_URL = 'http://www.igalia.com'

HOME_PATH = os.getenv('HOME')
SF_CONF_FOLDER = HOME_PATH + '/.osso/%s' % SF_COMPACT_NAME
SF_CONF_FILE = SF_CONF_FOLDER + '/%s.conf' % SF_COMPACT_NAME
SF_DB_FILE = SF_CONF_FOLDER + '/%s' % 'series.db'

DEFAULT_SYSTEM_APP_DIR = os.path.join(sys.prefix,
                                      'share',
                                      SF_COMPACT_NAME)
APP_DIR = DEFAULT_SYSTEM_APP_DIR

if not os.path.exists(APP_DIR):
    APP_DIR = os.path.dirname(os.path.dirname(__file__))
    APP_DIR = os.path.join(APP_DIR, 'data')

LOCALE_DIR = os.path.join(APP_DIR, 'locale')


DEFAULT_LANGUAGES = os.environ.get('LANGUAGE', '').split(':')
DEFAULT_LANGUAGES += ['en_US', 'pt_PT']

TVDB_API_KEY = 'FAD75AF31E1B1577'

SECONDARY_TEXT_COLOR = '#AFAFAF'
