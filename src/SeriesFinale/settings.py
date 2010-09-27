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
from lib import constants
from xml.etree import ElementTree as ET

class Settings(object):
    
    ASCENDING_ORDER = 0
    DESCENDING_ORDER = 1
    RECENT_EPISODE = 1

    EPISODES_ORDER_CONF_NAME = 'episodes_order'
    SHOWS_SORT = 'shows_sort'

    TYPES = {EPISODES_ORDER_CONF_NAME: int,
             SHOWS_SORT: int}
    DEFAULTS = {EPISODES_ORDER_CONF_NAME: DESCENDING_ORDER,
                SHOWS_SORT: RECENT_EPISODE,
                }

    conf = dict(DEFAULTS)

    def load(self, conf_file):
        if not (os.path.exists(conf_file) and os.path.isfile(conf_file)):
            return
        
        tree = ET.ElementTree()
        tree.parse(conf_file)
        root = tree.getroot()
        for key in self.DEFAULTS.keys():
            key_element = root.find(key)
            if key_element is not None:
                if self.TYPES[key] == bool:
                    self.setConf(key, key_element.text.lower() == 'true')
                    continue
                self.setConf(key, self.TYPES[key](key_element.text))

    def save(self, conf_file):
        root = ET.Element(constants.SF_COMPACT_NAME)
        for key, value in self.__class__.conf.items():
            element = ET.SubElement(root, key)
            element.text = str(value)
        return ET.ElementTree(root).write(conf_file, 'UTF-8')

    def setConf(self, key, value):
        self.__class__.conf[key] = value

    def getConf(self, key):
        return self.TYPES[key](self.__class__.conf[key])
