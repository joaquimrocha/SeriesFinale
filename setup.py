#!/usr/bin/env python

import sys
sys.path = ['src'] + sys.path
from distutils.core import setup
from SeriesFinale.lib import constants

setup(name = constants.SF_NAME.lower(),
     version = constants.SF_VERSION,
     description = constants.SF_DESCRIPTION,
     author = 'Joaquim Rocha',
     author_email = 'jrocha@igalia.com',
     url = constants.SF_URL,
     license = 'GPL v3',
     packages = ['SeriesFinale', 'SeriesFinale.lib',
                 'jsonpickle'],
     package_dir = {'': 'src'},
     scripts = ['seriesfinale'],
     data_files = [('/usr/share/icons/hicolor/scalable/apps', ['data/seriesfinale.png']
                   ),
                   ('/usr/share/applications/hildon', ['data/seriesfinale.desktop']
                   ),
                   ]
     )
