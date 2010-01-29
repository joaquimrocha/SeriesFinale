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

import jsonpickle
from xml.etree import ElementTree as ET

def serialize(show_list):
    for show in show_list:
        for episode in show.episode_list:
            episode.show = show.id
    return jsonpickle.encode(show_list)

def deserialize(shows_file_path):
    shows_file = open(shows_file_path, 'r')
    contents = shows_file.read()
    shows_file.close()
    shows_list = jsonpickle.decode(contents)
    for show in shows_list:
        for episode in show.episode_list:
            episode.show = show
            # IMPORTANT: The code below is here so the episode_number
            # is set using the right Episode object's property
            episode.episode_number = episode.episode_number
            # This prevents errors when the
            # stored objects still don't have
            # the air date variable
            try:
                episode.air_date
            except AttributeError:
                episode.air_date = ''
    return shows_list
