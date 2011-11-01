#!/usr/bin/env python

import sys
sys.path = ['src'] + sys.path
import glob
import os
from distutils.core import setup
from SeriesFinale.lib import constants

def get_locale_files():
    files = glob.glob('locale/*/*/*.mo')
    file_list = []
    for file in files:
        destination_file_name = os.path.join(constants.DEFAULT_SYSTEM_APP_DIR, file)
        file_list.append((os.path.dirname(destination_file_name), [file]))
    return file_list

def get_qml_files():
    files = glob.glob('qml/*.qml')
    file_list = []
    for file in files:
        destination_file_name = os.path.join(constants.DEFAULT_SYSTEM_APP_DIR, file)
        file_list.append((os.path.dirname(destination_file_name), [file]))
    return file_list

def get_qml_icon_files():
    files = glob.glob('qml/icons/*')
    file_list = []
    for file in files:
        destination_file_name = os.path.join(constants.DEFAULT_SYSTEM_APP_DIR, file)
        file_list.append((os.path.dirname(destination_file_name), [file]))
    return file_list

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
     data_files = [(constants.ICON_FOLDER, ['data/seriesfinale.png']
                   ),
                   ('share/applications', ['data/seriesfinale.desktop']
                   ),
                   (constants.DEFAULT_SYSTEM_APP_DIR, ['data/placeholderimage.png',
                                                       'data/downloadingimage.png',
                                                       'data/sf-splash-landscape.jpg',
                                                       'data/sf-splash-portrait.jpg']),
                   ] + get_locale_files() + get_qml_files() + get_qml_icon_files()
     )
