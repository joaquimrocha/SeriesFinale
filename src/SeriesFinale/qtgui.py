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

import gettext
import locale
import os
import re
import time
from xml.sax import saxutils
from series import SeriesManager, Show, Episode
from lib import constants
from lib.connectionmanager import ConnectionManager
from lib.portrait import FremantleRotation
from lib.util import get_color
from settings import Settings
from asyncworker import AsyncWorker, AsyncItem

_ = gettext.gettext
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import *

class MainWindow(QDeclarativeView):

    def __init__(self):
        QDeclarativeView.__init__(self)
        self.engine().quit.connect(self.close)

        # i18n
        languages = []
        lc, encoding = locale.getdefaultlocale()
        if lc:
            languages = [lc]
        languages += constants.DEFAULT_LANGUAGES
        gettext.bindtextdomain(constants.SF_COMPACT_NAME,
                               constants.LOCALE_DIR)
        gettext.textdomain(constants.SF_COMPACT_NAME)
        language = gettext.translation(constants.SF_COMPACT_NAME,
                                       constants.LOCALE_DIR,
                                       languages = languages,
                                       fallback = True)
        _ = language.gettext

        self.series_manager = SeriesManager()
        self.settings = Settings()
        load_conf_item = AsyncItem(self.settings.load,
                                   (constants.SF_CONF_FILE,),
                                   self._settings_load_finished)
        load_shows_item = AsyncItem(self.series_manager.load,
                                    (constants.SF_DB_FILE,),
                                    self._load_finished)

        self.request = AsyncWorker()
        self.request.queue.put((0, load_conf_item))
        self.request.queue.put((0, load_shows_item))
        self.request.start()

        self.setWindowTitle(constants.SF_NAME)
        settingsWrapper = SettingsWrapper(self)
        self.rootContext().setContextProperty("series_manager", self.series_manager)
        self.rootContext().setContextProperty("seriesList", self.series_manager.sorted_series_list)
        self.rootContext().setContextProperty("settings", settingsWrapper)
        settingsWrapper.showsSortChanged.connect(self.series_manager.sorted_series_list.resort)
        settingsWrapper.hideCompletedShowsChanged.connect(self.series_manager.sorted_series_list.resort)
        self.setSource(constants.QML_MAIN)
        self.showFullScreen()

    def closeEvent(self, event):
        self._exit_cb(event)

    def _settings_load_finished(self, dummy_arg, error):
        self.series_manager.sorted_series_list.resort()

    def _load_finished(self, dummy_arg, error):
        self.request = None
        self.series_manager.auto_save(True)

    @Slot()
    def _exit_cb(self, event):
        if self.request:
            self.request.stop()
        # If the shows list is empty but the user hasn't deleted
        # any, then we don't save in order to avoid overwriting
        # the current db (for the shows list might be empty due
        # to an error)
        if not self.series_manager.series_list and not self.series_manager.have_deleted:
            self.close()
            return
        self.series_manager.auto_save(False)

        save_shows_item = AsyncItem(self.series_manager.save,
                               (constants.SF_DB_FILE,))
        save_conf_item = AsyncItem(self.settings.save,
                               (constants.SF_CONF_FILE,),
                               self._save_finished_cb)
        async_worker = AsyncWorker()
        async_worker.queue.put((0, save_shows_item))
        async_worker.queue.put((0, save_conf_item))
        async_worker.start()
        event.ignore()

    def _save_finished_cb(self, dummy_arg, error):
        QApplication.instance().quit()

class SettingsWrapper(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    addSpecialSeasonsChanged = Signal()
    def getAddSpecialSeasons(self):
        return Settings().getConf(Settings.ADD_SPECIAL_SEASONS)
    def setAddSpecialSeasons(self, add):
        Settings().setConf(Settings.ADD_SPECIAL_SEASONS, add)
        self.addSpecialSeasonsChanged.emit()
    addSpecialSeasons = Property(bool,getAddSpecialSeasons,setAddSpecialSeasons,notify=addSpecialSeasonsChanged)

    hideCompletedShowsChanged = Signal()
    def getHideCompletedShows(self):
        logging.debug("Getting %i" % Settings().getConf(Settings.HIDE_COMPLETED_SHOWS))
        return Settings().getConf(Settings.HIDE_COMPLETED_SHOWS)
    def setHideCompletedShows(self, add):
        Settings().setConf(Settings.HIDE_COMPLETED_SHOWS, add)
        self.hideCompletedShowsChanged.emit()
    hideCompletedShows = Property(bool,getHideCompletedShows,setHideCompletedShows,notify=hideCompletedShowsChanged)

    episodesOrderChanged = Signal()
    def getEpisodesOrder(self):
        return Settings().getConf(Settings.EPISODES_ORDER_CONF_NAME)
    def setEpisodesOrder(self, newOrder):
        Settings().setConf(Settings.EPISODES_ORDER_CONF_NAME, newOrder)
        self.episodesOrderChanged.emit()
    episodesOrder = Property(int,getEpisodesOrder,setEpisodesOrder,notify=episodesOrderChanged)

    showsSortChanged = Signal()
    def getShowsSort(self):
        return Settings().getConf(Settings.SHOWS_SORT)
    def setShowsSort(self, newOrder):
        Settings().setConf(Settings.SHOWS_SORT, newOrder)
        self.showsSortChanged.emit()
    showsSort = Property(int,getShowsSort,setShowsSort,notify=showsSortChanged)
