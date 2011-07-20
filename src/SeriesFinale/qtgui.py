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
                                   (constants.SF_CONF_FILE,))
        load_shows_item = AsyncItem(self.series_manager.load,
                                    (constants.SF_DB_FILE,),
                                    self._load_finished)

        self.request = AsyncWorker()
        self.request.queue.put((0, load_conf_item))
        self.request.queue.put((0, load_shows_item))
        self.request.start()

        self.setWindowTitle(constants.SF_NAME)

    def _load_finished(self, dummy_arg, error):
        self.request = None
        self.series_manager.auto_save(True)

    def _exit_cb(self, window, event):
        if self.request:
            self.request.stop()
        # If the shows list is empty but the user hasn't deleted
        # any, then we don't save in order to avoid overwriting
        # the current db (for the shows list might be empty due
        # to an error)
        if not self.series_manager.series_list and not self._have_deleted:
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

    def _save_finished_cb(self, dummy_arg, error):
        hildon.hildon_gtk_window_set_progress_indicator(self, False)
        gtk.main_quit()

