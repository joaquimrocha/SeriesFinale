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
import gobject
from lib import thetvdbapi, serializer
from xml.etree import ElementTree as ET
from asyncworker import AsyncWorker
from lib.constants import TVDB_API_KEY
from datetime import datetime
import gettext

_ = gettext.gettext

class Show(object):
    
    def __init__(self, name, genre = None, overview = None, network = None,
                 rating = None, actors = [], episode_list = [], thetvdb_id = -1):
        self.id = -1
        self.name = name
        self.genre = genre
        self.overview = overview
        self.network = network
        self.rating = rating
        self.actors = actors
        self.episode_list = episode_list
        self.thetvdb_id = thetvdb_id
    
    def get_episodes_by_season(self, season_number):
        if season_number is None:
            return self.episode_list
        return [episode for episode in self.episode_list if episode.season_number == season_number]
    
    def get_seasons(self):
        seasons = []
        for episode in self.episode_list:
            season_number = episode.season_number
            if season_number not in seasons:
                seasons.append(season_number)
        return seasons
    
    def get_episode_list_by_season(self, season):
        return [episode for episode in self.episode_list \
                if episode.season_number == season]

    def update_episode_list(self, episode_list):
        for episode in episode_list:
            exists = False
            for ep in self.episode_list:
                if ep == episode:
                    exists = True
                    ep.merge_episode(episode)
            if not exists:
                self.episode_list.append(episode)
    
    def delete_episode(self, episode):
        for i in xrange(len(self.episode_list)):
            if self.episode_list[i] == episode:
                del self.episode_list[i]
                break
    
    def is_completely_watched(self):
        for episode in self.episode_list:
            if not episode.watched:
                return False
        return True

    def __str__(self):
        return self.name

class Episode(object):
    
    def __init__(self, name, show, episode_number, season_number = '1',
                 overview = None, director = None, guest_stars = [],
                 rating = None, writer = None, watched = False,
                 air_date = ''):
        self.id = -1
        self.name = name
        self.show = show
        self.episode_number = episode_number
        self.season_number = season_number
        self.overview = overview
        self.director = director
        self.guest_stars = guest_stars
        self.rating = rating
        self.writer = writer
        self.watched = watched
        self.air_date = air_date

    def __repr__(self):
        return _('Ep. %s: %s') % (self.episode_number, self.name)
    
    def __eq__(self, episode):
        if not episode:
            return False
        return self.show == episode.show and \
               self.episode_number == episode.episode_number and \
               self.season_number == episode.season_number and \
               self.name == episode.name
    
    def merge_episode(self, episode):
        self.name = self.name or episode.name
        self.show = self.show or episode.show
        self.episode_number = self.episode_number or episode.episode_number
        self.season_number = self.season_number or episode.season_number
        self.overview = self.overview or episode.overview
        self.director = self.director or episode.director
        self.guest_stars = self.guest_stars or episode.guest_stars
        self.rating = self.rating or episode.rating
        self.writer = self.writer or episode.writer
        self.watched = self.watched or episode.watched
        self.air_date = self.air_date or episode.air_date

    def _get_episode_number(self):
        return self._episode_number

    def _set_episode_number(self, number):
        try:
            self._episode_number = int(number)
        except ValueError:
            self._episode_number = 1
    
    episode_number = property(_get_episode_number, _set_episode_number)

class SeriesManager(gobject.GObject):
    
    SEARCH_SERIES_COMPLETE_SIGNAL = 'search-shows-complete'
    GET_FULL_SHOW_COMPLETE_SIGNAL = 'get-full-show-complete'
    UPDATE_SHOW_EPISODES_COMPLETE_SIGNAL = 'update-show-episodes-complete'
    SHOW_LIST_CHANGED_SIGNAL = 'show-list-changed'
    
    __gsignals__ = {SEARCH_SERIES_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                                    gobject.TYPE_NONE,
                                                    (gobject.TYPE_PYOBJECT,
                                                     gobject.TYPE_PYOBJECT)),
                    GET_FULL_SHOW_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                                    gobject.TYPE_NONE,
                                                    (gobject.TYPE_PYOBJECT,
                                                     gobject.TYPE_PYOBJECT)),
                    UPDATE_SHOW_EPISODES_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                                           gobject.TYPE_NONE,
                                                           (gobject.TYPE_PYOBJECT,
                                                            gobject.TYPE_PYOBJECT)),
                    SHOW_LIST_CHANGED_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                               gobject.TYPE_NONE,
                                               ()),
                   }
    
    def __init__(self):
        gobject.GObject.__init__(self)

        self.series_list = []

        self.thetvdb = thetvdbapi.TheTVDB(TVDB_API_KEY)
        self.async_worker = None
        
        # Cached values 
        self._cached_tvdb_shows = {}
    
    def search_shows(self, terms):
        if not terms:
            return []
        self.async_worker = AsyncWorker(self.thetvdb.get_matching_shows, terms, self._search_finished_callback)
        self.async_worker.start()
    
    def _search_finished_callback(self, tvdbshows, error):
        shows = []
        if not error:
            for show_id, show in tvdbshows:
                self._cached_tvdb_shows[show_id] = show
                shows.append(show)
        self.emit(self.SEARCH_SERIES_COMPLETE_SIGNAL, shows, error)
    
    def update_show_episodes(self, show):
        self.async_worker = AsyncWorker(self.thetvdb.get_show_and_episodes,
                                        show.thetvdb_id,
                                        self._get_show_episodes_complete_cb, (show,))
        self.async_worker.start()
    
    def _get_show_episodes_complete_cb(self, show, tvdbcompleteshow, error):
        if not error:
            episode_list = [self._convert_thetvdbepisode_to_episode(tvdb_ep,show) \
                            for tvdb_ep in tvdbcompleteshow[1]]
            show.update_episode_list(episode_list)
        self.emit(self.UPDATE_SHOW_EPISODES_COMPLETE_SIGNAL, show, error)
    
    def _search_show_to_update_callback(self, tvdbshows):
        if not tvdbshows:
            # FIXME: raise error
            return
        for show_id, show in tvdbshows:
            pass
    
    def get_complete_show(self, show_name):
        show_id = self._cached_tvdb_shows.get(show_name, None)
        for show_id, show_title in self._cached_tvdb_shows.items():
            if show_title == show_name:
                break 
        if not show_id:
            return
        self.async_worker = AsyncWorker(self.thetvdb.get_show_and_episodes,
                                        show_id,
                                        self._get_complete_show_finished_cb)
        self.async_worker.start()
    
    def _get_complete_show_finished_cb(self, tvdb_show_episodes, error):
        show = None
        if not tvdb_show_episodes:
            return
        if not error:
            show = self._convert_thetvdbshow_to_show(tvdb_show_episodes[0])
            show.id = self._get_id_for_show()
            show.episode_list = []
            for tvdb_ep in tvdb_show_episodes[1]:
                show.episode_list.append(self._convert_thetvdbepisode_to_episode(tvdb_ep,
                                                                                 show))
            self.series_list.append(show)
        self.emit(self.GET_FULL_SHOW_COMPLETE_SIGNAL, show, error)

    def get_show_by_id(self, show_id):
        for show in self.series_list:
            if show.id == show_id:
                return show
        return None
    
    def _convert_thetvdbshow_to_show(self, thetvdb_show):
        show_obj = Show(thetvdb_show.name)
        show_obj.genre = thetvdb_show.genre
        show_obj.overview = thetvdb_show.overview
        show_obj.network = thetvdb_show.network
        show_obj.rating = thetvdb_show.rating
        show_obj.actors = thetvdb_show.actors
        show_obj.thetvdb_id = thetvdb_show.id
        return show_obj

    def _convert_thetvdbepisode_to_episode(self, thetvdb_episode, show = None):
        episode_obj = Episode(thetvdb_episode.name, show, thetvdb_episode.episode_number)
        episode_obj.show = show
        episode_obj.season_number = thetvdb_episode.season_number
        episode_obj.overview = thetvdb_episode.overview
        episode_obj.director = thetvdb_episode.director
        episode_obj.guest_stars = thetvdb_episode.guest_stars
        episode_obj.rating = thetvdb_episode.rating
        episode_obj.writer = thetvdb_episode.writer
        episode_obj.air_date = thetvdb_episode.first_aired or ''
        return episode_obj
    
    def stop_request(self):
        self.async_worker.stopped = True
        self.async_worker = None
    
    def add_show(self, show):
        if show.id == -1:
            show.id = self._get_id_for_show()
        self.series_list.append(show)
        self.emit(self.SHOW_LIST_CHANGED_SIGNAL)
    
    def delete_show(self, show):
        for i in xrange(len(self.series_list)):
            if self.series_list[i] == show:
                del self.series_list[i]
                self.emit(self.SHOW_LIST_CHANGED_SIGNAL)
                break

    def _get_id_for_show (self):
        id = 1
        for show in self.series_list:
            id = show.id
            if show.id >= id:
                id += 1
        return id

    def save(self, save_file_path):
        dirname = os.path.dirname(save_file_path)
        if not (os.path.exists(dirname) and os.path.isdir(dirname)):
            os.mkdir(dirname)
        serialized = serializer.serialize(self.series_list)
        save_file = open(save_file_path, 'w')
        save_file.write(serialized)
        save_file.close()

    def load(self, file_path):
        if not os.path.exists(file_path):
            self.series_list = []
            return
        self.series_list = serializer.deserialize(file_path)
