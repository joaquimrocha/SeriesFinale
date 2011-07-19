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
import json
import SeriesFinale.series
from listmodel import ListModel
from xml.etree import ElementTree as ET

def serialize(show_list):
    return json.dumps(show_list, cls = ShowDecoder, indent = 4)

def deserialize(shows_file_path):
    shows_file = open(shows_file_path, 'r')
    contents = shows_file.read()
    shows_file.close()
    # The following test is to guarantee retro-compatibility with the
    # old jsonpickle generated json
    if contents.startswith('[{"py/object": "SeriesFinale.series.Show"'):
        return deserialize_from_old_format(contents)
    return json.loads(contents, object_hook = show_encoder)

def deserialize_from_old_format(contents):
    shows_list = jsonpickle.decode(contents)
    shows_json = json.dumps(shows_list, cls = ShowDecoder)
    return json.loads(shows_json, object_hook = show_encoder)

class ShowDecoder(json.JSONEncoder):

    def default(self, show):
        show_json = dict(show.__dict__)
        show_json['json_type'] = 'show'
        episode_list = show_json['episode_list']
        remove_private_vars(show_json)
        show_json['episode_list'] = [self._decode_episode(episode) \
                                     for episode in episode_list]
        if isinstance(show.actors, list):
            show_json['actors'] = '|'.join(show.actors)
        return show_json

    def _decode_episode(self, episode):
        episode_json = dict(episode.__dict__)
        episode_json['json_type'] = 'episode'
        del episode_json['show']
        episode_json['air_date'] = str(episode.air_date)
        episode_json['episode_number'] = str(episode.episode_number)
        remove_private_vars(episode_json)
        if isinstance(episode.guest_stars, list):
            episode_json['guest_stars'] = '|'.join(episode.guest_stars)
        return episode_json

def show_encoder(dictionary):
    if dictionary.get('json_type') != 'show':
        return dictionary
    name = dictionary['name']
    del dictionary['name']
    del dictionary['json_type']
    episode_list = list(dictionary['episode_list'])
    del dictionary['episode_list']
    show = SeriesFinale.series.Show(name, **dictionary)
    episode_list = ListModel([episode_encoder(show, episode) for episode in \
                     episode_list])
    show.episode_list = episode_list
    return show

def episode_encoder(show, dictionary):
    if dictionary.get('json_type') != 'episode':
        return dictionary
    name = dictionary['name']
    del dictionary['name']
    del dictionary['json_type']
    episode_number = dictionary['episode_number']
    del dictionary['episode_number']
    episode = SeriesFinale.series.Episode(name,
                                          show,
                                          episode_number,
                                          **dictionary)
    return episode

def remove_private_vars(dictionary):
    for key in dictionary.keys():
        if key[0] == '_':
            del dictionary[key]
