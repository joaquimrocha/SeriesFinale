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

import urllib
import urllib2
import os

def get_color(color_name):
    # Adapted from gPodder
    settings = gtk.settings_get_default()
    if not settings:
        return None
    color_style = gtk.rc_get_style_by_paths(settings,
                                            'GtkButton',
                                            'osso-logical-colors',
                                            gtk.Button)
    return color_style.lookup_color(color_name).to_string()

def image_downloader(url, save_name):
    image = urllib2.urlopen(url).read()
    path, format = os.path.splitext(url)
    target = save_name + format
    temp_target = target + '.tmp'
    image_file = open(temp_target, 'wb+')
    image_file.write(image)
    image_file.close()
    os.rename(temp_target, target)
    return target
