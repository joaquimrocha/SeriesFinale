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
    
    EPISODES_ORDER_CONF_NAME = 'episodes_order'
    
    def __init__(self):
        self.episodes_order = self.DESCENDING_ORDER
        
    def load(self, conf_file):
        if not (os.path.exists(conf_file) and os.path.isfile(conf_file)):
            return
        
        tree = ET.ElementTree()
        tree.parse(conf_file)
        root = tree.getroot()
        
        episodes_order = root.find(self.EPISODES_ORDER_CONF_NAME)
        if episodes_order != None:
            try:
                self.episodes_order = int(episodes_order.text)
            except ValueError:
                self.episodes_order = self.DESCENDING_ORDER
    
    def save(self, conf_file):
        root = ET.Element(constants.SF_COMPACT_NAME)
        episodes_order_element = ET.SubElement(root, self.EPISODES_ORDER_CONF_NAME)
        episodes_order_element.text = str(self.episodes_order)
        return ET.ElementTree(root).write(conf_file, 'UTF-8')