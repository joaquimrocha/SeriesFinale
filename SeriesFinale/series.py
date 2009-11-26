import gobject
from lib import thetvdbapi
from storm.locals import *
from xml.etree import ElementTree as ET
from asyncworker import AsyncWorker


TVDB_API_KEY = 'FAD75AF31E1B1577'

class Show(object):
    
    def __init__(self, name, genre = None, overview = None, network = None,
                 rating = None, actors = [], episode_list = []):
        self.name = name
        self.genre = genre
        self.overview = overview
        self.network = network
        self.rating = rating
        self.actors = actors
        self.episode_list = episode_list

    def __str__(self):
        return self.name

class Episode(object):
    
    def __init__(self, name, show, episode_number, season_number = 1,
                 overview = None, director = None, guest_stars = [],
                 rating = None, writer = None):
        self.name = name
        self.show = show
        self.episode_number = episode_number
        self.season_number = season_number
        self.overview = overview
        self.director = director
        self.guest_stars = guest_stars
        self.rating = rating
        self.writer = writer
    
    def __str__(self):
        return self.name

class SeriesManager(gobject.GObject):
    
    SEARCH_SERIES_COMPLETE_SIGNAL = 'search-series-complete'
    GET_FULL_SHOW_COMPLETE_SIGNAL = 'get-full-show-complete'
    
    __gsignals__ = {SEARCH_SERIES_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                                    gobject.TYPE_NONE,
                                                    (gobject.TYPE_PYOBJECT,)),
                    GET_FULL_SHOW_COMPLETE_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                                    gobject.TYPE_NONE,
                                                    (gobject.TYPE_PYOBJECT,)),
                   }
    
    def __init__(self):
        gobject.GObject.__init__(self)
        self.thetvdb = thetvdbapi.TheTVDB(TVDB_API_KEY)
        self.async_worker = None
        
        # Cached values 
        self._cached_tvdb_shows = {}
    
    def search_series(self, terms):
        if not terms:
            return []
        self.async_worker = AsyncWorker(self.thetvdb.get_matching_shows, terms, self._search_finished_callback)
        self.async_worker.start()
    
    def _search_finished_callback(self, tvdbshows):
        self.async_worker = None
        for show_id, show in tvdbshows:
            self._cached_tvdb_shows[show_id] = show
        self.emit(self.SEARCH_SERIES_COMPLETE_SIGNAL, self._cached_tvdb_shows.values())
    
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
    
    def _get_complete_show_finished_cb(self, tvdb_show_episodes):
        if not tvdb_show_episodes:
            return
        show = self._convert_thetvdbshow_to_show(tvdb_show_episodes[0])
        show.episode_list = []
        for tvdb_ep in tvdb_show_episodes[1]:
            show.episode_list.append(self._convert_thetvdbepisode_to_episode(tvdb_ep,
                                                                             show))
        self.emit(self.GET_FULL_SHOW_COMPLETE_SIGNAL, show)

    def _convert_thetvdbshow_to_show(self, thetvdb_show):
        show_obj = Show(thetvdb_show.name)
        show_obj.genre = thetvdb_show.genre
        show_obj.overview = thetvdb_show.overview
        show_obj.network = thetvdb_show.network
        show_obj.rating = thetvdb_show.rating
        show_obj.actors = thetvdb_show.actors
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
        return episode_obj

    def get_show_episodes(self, show):
        shows = self.thetvdb.get_matching_shows(show.name)
        if not shows:
            return []
        show_episodes = self.thetvdb.get_show_and_episodes(shows[0][0])[1]
        show_obj.episode_list = [self._convert_thetvdbepisode_to_episode(episode) for episode in show_episodes]
    
    def stop_request(self):
        self.async_worker.stopped = True
        self.async_worker = None
