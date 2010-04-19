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
from lib import thetvdbapi, serializer, constants
from lib.util import get_color, image_downloader
from xml.etree import ElementTree as ET
from asyncworker import AsyncWorker, AsyncItem
from lib.constants import TVDB_API_KEY, DATA_DIR
from datetime import datetime
from xml.sax import saxutils
import gettext

_ = gettext.gettext

class Show(object):
    
    def __init__(self, name, language = "en", genre = None, overview = None,
                 network = None, rating = None, actors = [], episode_list = [],
                 image = None, thetvdb_id = -1):
        self.id = -1
        self.name = name
        self.language = language
        self.genre = genre
        self.overview = overview
        self.network = network
        self.rating = rating
        self.actors = actors
        self.episode_list = episode_list
        self.image = image
        self.season_images = {}
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

    def get_episodes_info(self, season = None):
        info = {}
        episodes = self.episode_list
        if season:
            episodes = self.get_episode_list_by_season(season)
        episodes_to_watch = [episode for episode in episodes \
                            if not episode.watched]
        info['episodes'] = episodes
        info['episodes_to_watch'] = episodes_to_watch
        sorted_episodes_to_watch = [(episode.air_date, episode) \
                                    for episode in episodes_to_watch \
                                    if episode.air_date]
        sorted_episodes_to_watch.sort()
        info['next_episode'] = None
        if sorted_episodes_to_watch:
            info['next_episode'] = sorted_episodes_to_watch[0][1]
        return info

    def __str__(self):
        return self.name

    def get_info_markup(self):
        seasons = len(self.get_seasons())
        if seasons:
            color = get_color(constants.SECONDARY_TEXT_COLOR)
            episodes_info = self.get_episodes_info()
            episodes_to_watch = episodes_info['episodes_to_watch']
            next_episode = episodes_info['next_episode']
            if next_episode and next_episode.already_aired():
                color = get_color(constants.ACTIVE_TEXT_COLOR) 
            show_info = '\n<small><span foreground="%s">' % color
            show_info += gettext.ngettext('%s season', '%s seasons', seasons) \
                         % seasons
            if self.is_completely_watched():
                show_info += ' | ' + _('Completely watched')
            else:
                if episodes_to_watch:
                    n_episodes_to_watch = len(episodes_to_watch)
                    show_info += ' | ' + gettext.ngettext('%s episode not watched',
                                                          '%s episodes not watched',
                                                          n_episodes_to_watch) \
                                                          % n_episodes_to_watch
                    if next_episode:
                        next_air_date = next_episode.air_date
                        if next_air_date:
                            show_info += ' | ' + _('<i>Next air date:</i> ep. %s on %s') % \
                                         (next_episode.get_episode_show_number(), \
                                         next_episode.get_air_date_text())
                        else:
                            show_info += ' | ' + _('<i>Next to watch:</i> %s') % \
                                         saxutils.escape(str(next_episode))
                        if next_episode.already_aired():
                            color = get_color(constants.ACTIVE_TEXT_COLOR)
                else:
                    show_info += ' | ' + _('No episodes to watch')
            show_info += '</span></small>'
        else:
            show_info = ''
        return '<b>%s</b>' % saxutils.escape(self.name) + show_info

    def get_season_info_markup(self, season):
        if season == '0':
            name = _('Special')
        else:
            name = _('Season %s') % season
        info = self.get_episodes_info(season)
        episodes = info['episodes']
        episodes_to_watch = info['episodes_to_watch']
        next_episode = info['next_episode']
        season_info = ''
        color = get_color(constants.SECONDARY_TEXT_COLOR)
        if not episodes_to_watch:
            if episodes:
                name = '<small><span foreground="%s">%s</span></small>' % \
                        (get_color(constants.SECONDARY_TEXT_COLOR), name)
                season_info = _('Completely watched')
        else:
            number_episodes_to_watch = len(episodes_to_watch)
            season_info = gettext.ngettext('%s episode not watched',
                                           '%s episodes not watched',
                                           number_episodes_to_watch) \
                                           % number_episodes_to_watch
            if next_episode:
                next_air_date = next_episode.air_date
                if next_air_date:
                    season_info += ' | ' + _('<i>Next air date:</i> ep. %s on %s') % \
                                   (next_episode.episode_number, \
                                    next_episode.get_air_date_text())
                else:
                    season_info += ' | ' + _('<i>Next to watch:</i> %s') % \
                                   saxutils.escape(str(next_episode))
                if next_episode.already_aired():
                    color = get_color(constants.ACTIVE_TEXT_COLOR)
        return '<b>%s</b>\n<small><span foreground="%s">%s</span></small>' % \
               (name, color, season_info)


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

    def get_episode_show_number(self):
        return '%sx%02d' % (self.season_number, int(self.episode_number))

    def __repr__(self):
        return _('Ep. %s: %s') % (self.get_episode_show_number(), self.name)
    
    def __eq__(self, episode):
        if not episode:
            return False
        return self.show == episode.show and \
               self.episode_number == episode.episode_number and \
               self.season_number == episode.season_number
    
    def merge_episode(self, episode):
        self.name = episode.name or self.name
        self.show = episode.show or self.show
        self.episode_number = episode.episode_number or self.episode_number
        self.season_number = episode.season_number or self.season_number
        self.overview = episode.overview or self.overview
        self.director = episode.director or self.director
        self.guest_stars = episode.guest_stars or self.guest_stars
        self.rating = episode.rating or self.rating
        self.writer = episode.writer or self.writer
        self.watched = episode.watched or self.watched
        self.air_date = episode.air_date or self.air_date
    
    def get_air_date_text(self):
        if not self.air_date:
            return ''
        next_air_date_str = self.air_date.strftime('%d %b')
        if self.air_date.year != datetime.today().year:
            next_air_date_str += self.air_date.strftime(' %Y')
        return next_air_date_str
    
    def already_aired(self):
        if self.air_date and self.air_date <= datetime.today().date():
            return True
        return False
    
    def _get_episode_number(self):
        return self._episode_number

    def _set_episode_number(self, number):
        try:
            self._episode_number = int(number)
        except ValueError:
            self._episode_number = 1

    def _get_air_date(self):
        return self._air_date

    def _set_air_date(self, new_air_date):
        if type(new_air_date) != str:
            self._air_date = new_air_date
            return
        for format in ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y',
                       '%m-%d-%Y', '%d %b %Y']:
            try:
                self._air_date = datetime.strptime(new_air_date, format).date()
            except ValueError:
                continue
            else:
                return
        self._air_date = None

    def get_info_markup(self):
        color = get_color(constants.SECONDARY_TEXT_COLOR)
        if not self.watched and self.already_aired():
            color = get_color(constants.ACTIVE_TEXT_COLOR)
        return '<span foreground="%s">%s\n%s</span>' % \
               (color, saxutils.escape(str(self)), self.get_air_date_text())

    episode_number = property(_get_episode_number, _set_episode_number)
    air_date = property(_get_air_date, _set_air_date)

class SeriesManager(gobject.GObject):
    
    SEARCH_SERIES_COMPLETE_SIGNAL = 'search-shows-complete'
    GET_FULL_SHOW_COMPLETE_SIGNAL = 'get-full-show-complete'
    UPDATE_SHOW_EPISODES_COMPLETE_SIGNAL = 'update-show-episodes-complete'
    UPDATE_SHOWS_CALL_COMPLETE_SIGNAL = 'update-shows-call-complete'
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
                    UPDATE_SHOWS_CALL_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
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
        self.async_worker = AsyncWorker()
        async_item = AsyncItem(self.thetvdb.get_matching_shows,
                               (terms,),
                               self._search_finished_callback)
        self.async_worker.queue.put(async_item)
        self.async_worker.start()
    
    def _search_finished_callback(self, tvdbshows, error):
        shows = []
        if not error:
            for show_id, show in tvdbshows:
                self._cached_tvdb_shows[show_id] = show
                shows.append(show)
        self.emit(self.SEARCH_SERIES_COMPLETE_SIGNAL, shows, error)

    def update_show_episodes(self, show):
        return self.update_all_shows_episodes([show])

    def update_all_shows_episodes(self, show_list = []):
        show_list = show_list or self.series_list
        async_worker = AsyncWorker()
        i = 0
        n_shows = len(show_list)
        for i in range(n_shows):
            show = show_list[i]
            async_item = AsyncItem(self._set_show_images,
                                   (show,),
                                   None,)
            async_worker.queue.put(async_item)
            async_item = AsyncItem(self.thetvdb.get_show_and_episodes,
                                   (show.thetvdb_id, show.language,),
                                   self._set_show_episodes_complete_cb,
                                   (show, i == n_shows - 1))
            async_worker.queue.put(async_item)
        async_worker.start()
        return async_worker

    def _set_show_episodes_complete_cb(self, show, last_call, tvdbcompleteshow, error):
        if not error:
            episode_list = [self._convert_thetvdbepisode_to_episode(tvdb_ep,show) \
                            for tvdb_ep in tvdbcompleteshow[1]]
            show.update_episode_list(episode_list)
        self.emit(self.UPDATE_SHOW_EPISODES_COMPLETE_SIGNAL, show, error)
        if last_call:
            self.emit(self.UPDATE_SHOWS_CALL_COMPLETE_SIGNAL, show, error)
    
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
        self.async_worker = AsyncWorker()
        async_item = AsyncItem(self._get_complete_show_from_id,
                               (show_id,),
                               self._get_complete_show_finished_cb)
        self.async_worker.queue.put(async_item)
        self.async_worker.start()

    def _get_complete_show_from_id(self, show_id):
        tvdb_show_episodes = self.thetvdb.get_show_and_episodes(show_id)
        if not tvdb_show_episodes:
            return None
        show = self._convert_thetvdbshow_to_show(tvdb_show_episodes[0])
        show.id = self._get_id_for_show()
        show.episode_list = []
        for tvdb_ep in tvdb_show_episodes[1]:
            show.episode_list.append(self._convert_thetvdbepisode_to_episode(tvdb_ep,
                                                                             show))
        self.series_list.append(show)
        self._set_show_images(show)
        return show

    def _get_complete_show_finished_cb(self, show, error):
        self.emit(self.GET_FULL_SHOW_COMPLETE_SIGNAL, show, error)

    def get_show_by_id(self, show_id):
        for show in self.series_list:
            if show.id == show_id:
                return show
        return None
    
    def get_show_by_name(self, show_name):
        for show in self.series_list:
            if show.name == show_name:
                return show
        return None

    def _convert_thetvdbshow_to_show(self, thetvdb_show):
        show_obj = Show(thetvdb_show.name)
        show_obj.language = thetvdb_show.language
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
        if self.async_worker:
            self.async_worker.stop()
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

    def _set_show_images(self, show):
        thetvdb_id = show.thetvdb_id
        if thetvdb_id == -1:
            return
        image_choices = self.thetvdb.get_show_image_choices(thetvdb_id)
        seasons = show.get_seasons()
        for key, image in show.season_images.items():
            if not os.path.isfile(image):
                del show.season_images[key]
        for image in image_choices:
            image_type = image[1]
            url = image[0]
            if image_type  == 'poster' and \
               (not show.image or not os.path.isfile(show.image)):
                target_file = os.path.join(DATA_DIR, show.thetvdb_id)
                image_file = os.path.abspath(image_downloader(url, target_file))
                show.image = image_file
            elif image_type == 'season':
                season = image[3]
                if season in seasons and \
                   season not in show.season_images.keys():
                    target_file = os.path.join(DATA_DIR,
                                          show.thetvdb_id + '_season_' + season)
                    image_file = os.path.abspath(image_downloader(url,
                                                                  target_file))
                    show.season_images[season] = image_file
            if show.image and len(show.season_images) == len(seasons):
                break

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
