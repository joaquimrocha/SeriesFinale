# -*- coding: utf-8 -*-

###########################################################################
#    SeriesFinale
#    Copyright (C) 2009 Joaquim Rocha <jrocha@igalia.com>
#    Diablo version: Juan A. Suarez Romero <jasuarez@igalia.com>
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

import hildon
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext
import locale
import pango
from series import SeriesManager, Show, Episode
from lib import constants
from settings import Settings
from asyncworker import AsyncWorker, AsyncItem

_ = gettext.gettext

gtk.gdk.threads_init()

class MainWindow(hildon.Window):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
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
	self.progress = show_progress(self, _('Loading...'))
        load_shows_item = AsyncItem(self.series_manager.load,
                                    (constants.SF_DB_FILE,))
        self.series_manager.connect('show-list-changed',
                                    self._show_list_changed_cb)
        self.series_manager.connect('get-full-show-complete',
                                    self._get_show_complete_cb)
        self.series_manager.connect('update-show-episodes-complete',
                                    self._update_show_complete_cb)
        self.series_manager.connect('update-shows-call-complete',
                                    self._update_all_shows_complete_cb)
        
        self.settings = Settings()
        load_conf_item = AsyncItem(self.settings.load,
                                    (constants.SF_CONF_FILE,),
                                    self._load_finished)
        self.request = AsyncWorker()
        self.request.queue.put(load_shows_item)
        self.request.queue.put(load_conf_item)
        self.request.start()

        self.shows_view = ShowsSelectView()
        self.shows_view.connect('row-activated', self._row_activated_cb)
        self.set_title(constants.SF_NAME)
        self.set_menu(self._create_menu())
        winscroll = gtk.ScrolledWindow()
        winscroll.add(self.shows_view)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(winscroll)
        
        self.connect('delete-event', self._exit_cb)
        self._update_delete_menu_visibility()

    def _load_finished(self, dummy_arg, error):
        self.shows_view.set_shows(self.series_manager.series_list)
	self.progress.destroy()
        self.request = None
        self._update_delete_menu_visibility()

    def _create_menu(self):
        menu = gtk.Menu()
        
        menuitem = gtk.MenuItem(_('Add Shows'))
        menuitem.connect('activate', self._add_shows_cb)
        menu.append(menuitem)
        
        self.delete_menu = gtk.MenuItem(_('Delete Shows'))
        self.delete_menu.connect('activate', self._delete_shows_cb)
        menu.append(self.delete_menu)

        self.update_all_menu = gtk.MenuItem(_('Update All'))
        self.update_all_menu.connect('activate', self._update_all_shows_cb)
        menu.append(self.update_all_menu)

        menu.show_all()
        return menu
    
    def _add_shows_cb(self, button):
        new_show_dialog = NewShowsDialog()
        response = new_show_dialog.run()
        new_show_dialog.destroy()
        if response == NewShowsDialog.ADD_AUTOMATICALLY_RESPONSE:
            self._launch_search_shows_dialog()
        elif response == NewShowsDialog.ADD_MANUALLY_RESPONSE:
            self._new_show_dialog()
    
    def _delete_shows_cb(self, button):
        selection = self.shows_view.get_selection()
        selected_rows = selection.get_selected_rows()
        model, paths = selected_rows
        if not paths:
            show_information(self, _('Please select one or more shows'))
            return
        for path in paths:
            self.series_manager.delete_show(model[path][1])
    
    def _launch_search_shows_dialog(self):
        search_dialog = SearchShowsDialog(self, self.series_manager)
        response = search_dialog.run()
        show = None
        if response == gtk.RESPONSE_ACCEPT:
            if search_dialog.chosen_show:
                self.progress = show_progress(self,
                                              _('Gathering show information. Please wait...'))
                self.series_manager.get_complete_show(search_dialog.chosen_show)
        search_dialog.destroy()
        
    def _get_show_complete_cb(self, series_manager, show, error):
        if error:
            error_message = ''
            if 'socket' in str(error).lower():
                error_message = '\n ' + _('Please verify your internet connection '
                                          'is available')
                show_information(self,
                                 _('An error occurred.%s') % error_message)
        else:
            self.shows_view.set_shows(self.series_manager.series_list)
            self._update_delete_menu_visibility()
        self.progress.destroy()
    
    def _row_activated_cb(self, view, path, column):
        show = self.shows_view.get_show_from_path(path)
        seasons_view = SeasonsView(self.settings, self.series_manager, show)
        seasons_view.connect('delete-event',
                     lambda w, e:
                        self.shows_view.set_shows(self.series_manager.series_list))
        seasons_view.show_all()

    def _new_show_dialog(self):
        new_show_dialog = NewShowDialog(self)
        response = new_show_dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            show_info = new_show_dialog.get_info()
            show = Show(show_info['name'])
            show.overview = show_info['overview']
            show.genre = show_info['genre']
            show.network = show_info['network']
            show.rating = show_info['rating']
            show.actors = show_info['actors']
            self.series_manager.add_show(show)
        new_show_dialog.destroy()
    
    def _exit_cb(self, window, event):
        if self.request:
            self.request.stop()
	self.progress = show_progress(self, _('Saving...'))
        save_shows_item = AsyncItem(self.series_manager.save,
                               (constants.SF_DB_FILE,))
        save_conf_item = AsyncItem(self.settings.save,
                               (constants.SF_CONF_FILE,),
                               self._save_finished_cb)
        async_worker = AsyncWorker()
        async_worker.queue.put(save_shows_item)
        async_worker.queue.put(save_conf_item)
        async_worker.start()

    def _save_finished_cb(self, dummy_arg, error):
	self.progress.destroy()
        gtk.main_quit()

    def _show_list_changed_cb(self, series_manager):
        self.shows_view.set_shows(self.series_manager.series_list)
        self._update_delete_menu_visibility()
        return False
    
    def _update_delete_menu_visibility(self):
        if not self.series_manager.series_list or self.request:
            self.delete_menu.hide()
            self.update_all_menu.hide()
        else:
            self.delete_menu.show()
            self.update_all_menu.show()

    def _update_all_shows_cb(self, button):
	self.progress = show_progress(self, _('Updating all shows...'))
        self.request = self.series_manager.update_all_shows_episodes()
        self.set_sensitive(False)
        self._update_delete_menu_visibility()

    def _update_all_shows_complete_cb(self, series_manager, show, error):
        self._show_list_changed_cb(self.series_manager)
        if self.request:
            if error:
                show_information(self, _('Please verify your internet connection '
                                         'is available'))
            else:
                show_information(self, _('Finished updating the shows'))
        self.request = None
        self.set_sensitive(True)
        self._update_delete_menu_visibility()
	self.progress.destroy()

    def _update_show_complete_cb(self, series_manager, show, error):
        show_information(self, _('Updated "%s"') % show.name)

class ShowsSelectView(gtk.TreeView):
    
    SHOW_NAME_COLUMN = 0
    SHOW_OBJECT_COLUMN = 1
    
    def __init__(self):
        super(ShowsSelectView, self).__init__()
        model = gtk.ListStore(str, gobject.TYPE_PYOBJECT)
        show_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Name', show_renderer, text = self.SHOW_NAME_COLUMN)
        column.set_cell_data_func(show_renderer, self._show_select_view_data_func)
        self.set_model(model)
        self.append_column(column)
        self.sort_ascending()

    def set_shows(self, shows):
        model = self.get_model()
        model.clear()
        for show in shows:
            row = {self.SHOW_NAME_COLUMN: show.name,
                   self.SHOW_OBJECT_COLUMN: show
                  }
            model.append(row.values())

    def get_show_from_path(self, path):
        model = self.get_model()
        return model[path][self.SHOW_OBJECT_COLUMN]
    
    def sort_descending(self):
        self.get_model().set_sort_column_id(self.SHOW_NAME_COLUMN, gtk.SORT_DESCENDING)
    
    def sort_ascending(self):
        self.get_model().set_sort_column_id(self.SHOW_NAME_COLUMN, gtk.SORT_ASCENDING)
    
    def _show_select_view_data_func(self, column, renderer, model, iter):
        show = model.get_value(iter, self.SHOW_OBJECT_COLUMN)
        if not show:
            return
        seasons = len(show.get_seasons())
        if seasons:
            color = get_color(constants.SECONDARY_TEXT_COLOR)
            episodes_info = show.get_episodes_info()
            episodes_to_watch = episodes_info['episodes_to_watch']
            next_episode = episodes_info['next_episode']
            if next_episode and next_episode.already_aired():
                color = get_color(constants.DEFAULT_TEXT_COLOR) 
            show_info = '<small><span foreground="%s">' % color
            show_info += gettext.ngettext('%s season', '%s seasons', seasons) \
                         % seasons
            if show.is_completely_watched():
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
                            show_info += ' | ' + _('<i>Next air date:</i> %s') % \
                                         next_episode.get_air_date_text()
                        else:
                            show_info += ' | ' + _('<i>Next to watch:</i> %s') % \
                                         next_episode
                        if next_episode.already_aired():
                            color = get_color(constants.DEFAULT_TEXT_COLOR)
                else:
                    show_info += ' | ' + _('No episodes to watch')
            show_info += '</span></small>'
        else:
            show_info = ''
        renderer.set_property('markup',
                              '<b>%s</b>\n' % show.name +
                              show_info)
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)

class SeasonsView(hildon.Window):
    
    def __init__(self, settings, series_manager, show):
        super(SeasonsView, self).__init__()
        self.set_title(show.name)
        
        self.settings = settings
        
        self.series_manager = series_manager
        self.series_manager.connect('update-show-episodes-complete',
                                    self._update_show_episodes_complete_cb)
        self.show = show
        self.set_menu(self._create_menu())
        self.set_title(show.name)

        self.seasons_select_view = SeasonSelectView(self.show)
        seasons = self.show.get_seasons()
        self.seasons_select_view.set_seasons(seasons)
        self.seasons_select_view.connect('row-activated', self._row_activated_cb)
        self.connect('delete-event', self._delete_event_cb)
        
        winscroll = gtk.ScrolledWindow()
        winscroll.add(self.seasons_select_view)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(winscroll)
    
        self.request = None
        self._update_menu_visibility()

    def _delete_event_cb(self, window, event):
        if self.request:
            self.request.stop()
            self.request = None
        return False

    def _row_activated_cb(self, view, path, column):
        season = self.seasons_select_view.get_season_from_path(path)
        episodes_view = EpisodesView(self.settings, self.show, season)
        episodes_view.connect('delete-event', self._update_series_list_cb)
        episodes_view.connect('episode-list-changed', self._update_series_list_cb)
        episodes_view.show_all()

    def _update_series_list_cb(self, widget, event = None):
        seasons = self.show.get_seasons();
        self.seasons_select_view.set_seasons(seasons)
        self._update_menu_visibility()
    
    def _create_menu(self):
        menu = gtk.Menu()
        
        menuitem = gtk.MenuItem(_('Info'))
        menuitem.connect('activate', self._show_info_cb)
        menu.append(menuitem)
        
        menuitem = gtk.MenuItem(_('Edit Info'))
        menuitem.connect('activate', self._edit_show_info)
        menu.append(menuitem)
        
        if str(self.show.thetvdb_id) != '-1':
            self.update_menu = gtk.MenuItem(_('Update Show'))
            self.update_menu.connect('activate', self._update_series_cb)
            menu.append(self.update_menu)
        
        menuitem = gtk.MenuItem(_('New Episode'))
        menuitem.connect('activate', self._new_episode_cb)
        menu.append(menuitem)
        
        menu.show_all()
        return menu

    def _update_menu_visibility(self):
        if self.request or not self.show.get_seasons():
            self.update_menu.hide()
        else:
            self.update_menu.show()

    def _update_series_cb(self, button):
        self.request = self.series_manager.update_show_episodes(self.show)
        self.progress = show_progress(self, _('Updating show. Please wait...'))
        self.set_sensitive(False)
        self._update_menu_visibility()
    
    def _show_info_cb(self, button):
        dialog = gtk.Dialog(parent = self,
                            buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.set_title(_('Show Details'))
        dialog.set_default_size(600, 400);
        infotextview = InfoTextView()
        infotextview.set_title(self.show.name)
        infotextview.add_field (self.show.overview)
        infotextview.add_field ('\n')
        infotextview.add_field (self.show.genre, _('Genre'))
        infotextview.add_field (self.show.network, _('Network'))
        infotextview.add_field (self.show.actors, _('Actors'))
        infotextview.add_field (self.show.rating, _('Rating'))
        winscroll = gtk.ScrolledWindow()
        winscroll.add(infotextview)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        dialog.vbox.add(winscroll)
        dialog.vbox.show_all()
        dialog.run()
        dialog.destroy()
    
    def _edit_show_info(self, button):
        edit_series_dialog = EditShowsDialog(self, self.show)
        response = edit_series_dialog.run()
        info = edit_series_dialog.get_info()
        edit_series_dialog.destroy()
        if response == gtk.RESPONSE_ACCEPT:
            self.show.name = info['name']
            self.show.overview = info['overview']
            self.show.genre = info['genre']
            self.show.network = info['network']
            self.show.rating = info['rating']
            self.show.actors = info['actors']
        self.set_title(self.show.name)
    
    def _new_episode_cb(self, button):
        new_episode_dialog = NewEpisodeDialog(self,
                                              self.show)
        response = new_episode_dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            episode_info = new_episode_dialog.get_info()
            episode = Episode(episode_info['name'],
                              self.show,
                              episode_info['number'])
            episode.overview = episode_info['overview']
            episode.season_number = episode_info['season']
            episode.episode_number = episode_info['number']
            episode.director = episode_info['director']
            episode.writer = episode_info['writer']
            episode.rating = episode_info['rating']
            episode.air_date = episode_info['air_date']
            episode.guest_stars = episode_info['guest_stars']
            self.show.update_episode_list([episode])
            seasons = self.show.get_seasons()
            self.seasons_select_view.set_seasons(seasons)
        new_episode_dialog.destroy()
    
    def _update_show_episodes_complete_cb(self, series_manager, show, error):
        if error and self.request:
            error_message = ''
            if 'socket' in str(error).lower():
                error_message = '\n ' + _('Please verify your internet connection '
                                          'is available')
            show_information(self, error_message)
        elif show == self.show:
            seasons = self.show.get_seasons()
            model = self.seasons_select_view.get_model()
            if model:
                model.clear()
                self.seasons_select_view.set_seasons(seasons)
        self.progress.destroy()
        self.set_sensitive(True)
        self.request = None
        self._update_menu_visibility()
    
class SeasonSelectView(gtk.TreeView):
    
    SEASON_NAME_COLUMN = 0
    SEASON_NUMBER_COLUMN = 1
    
    def __init__(self, show):
        super(SeasonSelectView, self).__init__()
        self.show = show
        model = gtk.ListStore(str, str)
        season_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Name', season_renderer, text = 0)
        column.set_cell_data_func(season_renderer,
                                  self._season_select_view_data_func)
        self.set_model(model)
        self.append_column(column)

    def set_seasons(self, season_list):
        model = self.get_model()
        model.clear()
        for season in season_list:
            if season == '0':
                name = _('Special')
            else:
                name = _('Season %s') % season
            row = {self.SEASON_NAME_COLUMN: name,
                   self.SEASON_NUMBER_COLUMN: season,
                  }
            model.append(row.values())
    
    def get_season_from_path(self, path):
        model = self.get_model()
        iter = model.get_iter(path)
        season = model.get_value(iter, self.SEASON_NUMBER_COLUMN)
        return season
    
    def _season_select_view_data_func(self, column, renderer, model, iter):
        season = model.get_value(iter, self.SEASON_NUMBER_COLUMN)
        if season == '0':
            name = _('Special')
        else:
            name = _('Season %s') % season
        info = self.show.get_episodes_info(season)
        episodes = info['episodes']
        episodes_to_watch = info['episodes_to_watch']
        next_episode = info['next_episode']
        season_info = ''
        color = get_color(constants.SECONDARY_TEXT_COLOR)
        if not episodes_to_watch:
            if episodes:
                name = '<span foreground="%s">%s</span>' % \
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
                    season_info += ' | ' + _('<i>Next air date:</i> %s') % next_episode.get_air_date_text()
                else:
                    season_info += ' | ' + _('<i>Next to watch:</i> %s') % next_episode
                if next_episode.already_aired():
                    color = get_color(constants.DEFAULT_TEXT_COLOR)
        renderer.set_property('markup',
                              '<b>%s</b>\n'
                              '<span foreground="%s">%s</span>' % \
                              (name, color, season_info))
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)

class NewShowDialog(gtk.Dialog):
    
    def __init__(self, parent):
        super(NewShowDialog, self).__init__(parent = parent,
                                            buttons = (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT,
                                                       gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        
        self.set_title(_('Edit Show'))
        self.set_default_size(600, -1);
        self.show_name = gtk.Entry()
        self.show_overview = gtk.TextView()
        self.show_overview.set_wrap_mode(gtk.WRAP_WORD)
        self.show_genre = gtk.Entry()
        self.show_network = gtk.Entry()
        self.show_rating = gtk.Entry()
        self.show_actors = gtk.Entry()
        
        winscroll = gtk.ScrolledWindow()
        winscroll.add(self.show_overview)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        contents = gtk.VBox(False, 0)
        
        row = gtk.HBox(False, 12)
        row.pack_start(gtk.Label(_('Name:')), False, False, 0)
        row.pack_start(self.show_name, True, True, 0)
        contents.pack_start(row, False, False, 0)
        contents.pack_start(winscroll, False, False, 0)
        
        fields = [(_('Genre:'), self.show_genre),
                  (_('Network:'), self.show_network),
                  (_('Rating:'), self.show_rating),
                  (_('Actors:'), self.show_actors),
                 ]
        size_group = gtk.SizeGroup(gtk.SIZE_GROUP_BOTH)
        for text, widget in fields:
            row = gtk.HBox(False, 12)
            label = gtk.Label(text)
            size_group.add_widget(label)
            row.pack_start(label, False, False, 0)
            row.pack_start(widget, True, True, 0)
            contents.pack_start(row, False, False, 0)
                
        self.vbox.add(contents)
        self.vbox.show_all()
    
    def get_info(self):
        buffer = self.show_overview.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        overview_text = buffer.get_text(start_iter, end_iter)
        info = {'name': self.show_name.get_text(),
                'overview': overview_text,
                'genre': self.show_genre.get_text(),
                'network': self.show_network.get_text(),
                'rating': self.show_rating.get_text(),
                'actors': self.show_actors.get_text()}
        return info

class EditShowsDialog(NewShowDialog):
    
    def __init__(self, parent, show):
        super(EditShowsDialog, self).__init__(parent)
        
        self.show_name.set_text(show.name)
        self.show_overview.get_buffer().set_text(show.overview)
        self.show_genre.set_text(str(show.genre))
        self.show_network.set_text(show.network)
        self.show_rating.set_text(show.rating)
        self.show_actors.set_text(str(show.actors))

class NewEpisodeDialog(gtk.Dialog):
    
    def __init__(self, parent, show):
        super(NewEpisodeDialog, self).__init__(parent = parent,
                                               buttons = (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT,
                                                          gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        
        self.set_title(_('New Episode'))
        self.set_default_size(600, 400);

        self.episode_name = gtk.Entry()
        self.episode_overview = gtk.TextView()
        self.episode_overview.set_wrap_mode(gtk.WRAP_WORD)
        
        winscroll = gtk.ScrolledWindow()
        winscroll.add(self.episode_overview)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        self.episode_number = gtk.combo_box_entry_new_text()
        self.episode_number.set_title(_('Number:'))
        for i in xrange(20):
            self.episode_number.append_text(str(i + 1))
        self.episode_number.set_active(0)

        self.episode_season = gtk.combo_box_entry_new_text()
        self.episode_season.set_title(_('Season:'))
        seasons = show.get_seasons()
        for season in seasons:
            self.episode_season.append_text(season)
        if seasons:
            self.episode_season.set_active(len(seasons) - 1)
        else:
            self.episode_season.append_text('1')
            self.episode_season.set_active(0)
        
        self.episode_director = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_writer = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_air_date = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_rating = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_guest_stars = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        
        contents = gtk.VBox(False, 0)
        
        row = gtk.HBox(False, 12)
        row.pack_start(gtk.Label(_('Name:')), False, False, 0)
        row.pack_start(self.episode_name, True, True, 0)
        contents.pack_start(row, False, False, 0)
        contents.pack_start(winscroll, False, False, 0)
        row = gtk.HBox(False, 12)
        row.add(self.episode_season)
        row.add(self.episode_number)
        contents.pack_start(row, False, False, 0)
        
        fields = [(_('Director:'), self.episode_director),
                  (_('Writer:'), self.episode_writer),
                  (_('Original air date:'), self.episode_air_date),
                  (_('Rating:'), self.episode_rating),
                  (_('Guest Stars:'), self.episode_guest_stars),
                 ]
        size_group = gtk.SizeGroup(gtk.SIZE_GROUP_BOTH)
        for text, widget in fields:
            row = gtk.HBox(False, 12)
            label = gtk.Label(text)
            size_group.add_widget(label)
            row.pack_start(label, False, False, 0)
            row.pack_start(widget, True, True, 0)
            contents.pack_start(row, False, False, 0)
        
        self.vbox.add(contents)
        self.vbox.show_all()
    
    def get_info(self):
        buffer = self.episode_overview.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        overview_text = buffer.get_text(start_iter, end_iter)
        info = {'name': self.episode_name.get_text(),
                'overview': overview_text,
                'season': self.episode_season.child.get_text(),
                'number': self.episode_number.child.get_text(),
                'director': self.episode_director.get_text(),
                'writer': self.episode_writer.get_text(),
                'air_date': self.episode_air_date.get_text(),
                'rating': self.episode_rating.get_text(),
                'guest_stars': self.episode_guest_stars.get_text()}
        return info

class EditEpisodeDialog(NewEpisodeDialog):
    
    def __init__(self, parent, episode):
        super(EditEpisodeDialog, self).__init__(parent, episode.show)
        
        self.episode_name.set_text(episode.name)
        self.episode_overview.get_buffer().set_text(episode.overview)
        self.episode_season.child.set_text(episode.season_number)
        self.episode_number.child.set_text(str(episode.episode_number))
        self.episode_director.set_text(episode.director)
        self.episode_writer.set_text(str(episode.writer))
        self.episode_air_date.set_text(str(episode.air_date))
        self.episode_rating.set_text(episode.rating)
        self.episode_guest_stars.set_text(str(episode.guest_stars))

class EpisodesView(hildon.Window):
    
    EPISODES_LIST_CHANGED_SIGNAL = 'episode-list-changed'
    
    __gsignals__ = {EPISODES_LIST_CHANGED_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                                   gobject.TYPE_NONE,
                                                   ()),
                   }
    
    def __init__(self, settings, show, season_number = None):
        super(EpisodesView, self).__init__()
        
        self.settings = settings
        
        self.show = show
        self.season_number = season_number
        self.set_title(self.show.name)
        self.episodes_check_view = EpisodesCheckView()
        self.episodes_check_view.set_episodes(self.show.get_episodes_by_season(self.season_number))
        self.episodes_check_view.watched_renderer.connect('toggled',
                                                          self._watched_renderer_toggled_cb,
                                                          self.episodes_check_view.get_model())
        self.episodes_check_view.connect('row-activated', self._row_activated_cb)
        
        winscroll = gtk.ScrolledWindow()
        winscroll.add(self.episodes_check_view)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(winscroll)
        self.set_menu(self._create_menu())
	if self.settings.episodes_order == self.settings.ASCENDING_ORDER:
		self._sort_ascending_cb(None)
	else:
	        self._sort_descending_cb(None)
    
    def _create_menu(self):
        menu = gtk.Menu()
        
        menuitem = gtk.RadioMenuItem(label = _('A-Z'))
        menuitem.connect('activate', self._sort_ascending_cb)
        menu.append(menuitem)
	if self.settings.episodes_order == self.settings.ASCENDING_ORDER:
		menuitem.set_active(True)

        menuitem = gtk.RadioMenuItem(label = _('Z-A'), group = menuitem)
        menuitem.connect('activate', self._sort_descending_cb)
        menu.append(menuitem)
        if self.settings.episodes_order == self.settings.DESCENDING_ORDER:
		menuitem.set_active(True)

        menuitem = gtk.MenuItem(_('Mark All'))
        menuitem.connect('activate', self._select_all_cb)
        menu.append(menuitem)
        
        menuitem= gtk.MenuItem(_('Mark None'))
        menuitem.connect('activate', self._select_none_cb)
        menu.append(menuitem)

        menuitem = gtk.MenuItem(_('Delete Episodes'))
        menuitem.connect('activate', self._delete_episodes_cb)
        menu.append(menuitem)

        menu.show_all()
        return menu
    
    def _delete_episodes_cb(self, button):
        selection = self.episodes_check_view.get_selection()
        selected_rows = selection.get_selected_rows()
        model, paths = selected_rows
        if not paths:
            show_information(self, _('Please select one or more episodes'))
            return
        for path in paths:
            self.show.delete_episode(model[path][2])
        self._update_episodes_list_cb(None, None);
    
    def _select_all_cb(self, button):
        self.episodes_check_view.select_all()
    
    def _select_none_cb(self, button):
        self.episodes_check_view.select_none()
    
    def _row_activated_cb(self, view, path, column):
        episode = self.episodes_check_view.get_episode_from_path(path)
        if self.episodes_check_view.get_column(1) == column:
            episodes_view = EpisodeView(episode)
            episodes_view.connect('delete-event', self._update_episodes_list_cb)
            episodes_view.show_all()
    
    def _update_episodes_list_cb(self, widget, event = None):
        self.emit(self.EPISODES_LIST_CHANGED_SIGNAL)
        episodes = self.show.get_episodes_by_season(self.season_number)
        if episodes:
            self.episodes_check_view.set_episodes(episodes)
        else:
            self.destroy()
        return False
    
    def _watched_renderer_toggled_cb(self, renderer, path, model):
        episode = self.episodes_check_view.get_episode_from_path(path)
        episode.watched = not episode.watched
        model[path][0] = episode.watched
    
    def _sort_ascending_cb(self, button):
        self.episodes_check_view.sort_ascending()
        self.settings.episodes_order = self.settings.ASCENDING_ORDER
    
    def _sort_descending_cb(self, button):
        self.episodes_check_view.sort_descending()
        self.settings.episodes_order = self.settings.DESCENDING_ORDER

class EpisodesCheckView(gtk.TreeView):
    
    EPISODE_CHECK_COLUMN = 0
    EPISODE_NAME_COLUMN = 1
    EPISODE_OBJECT_COLUMN = 2
    
    def __init__(self):
        super(EpisodesCheckView, self).__init__()
        model = gtk.ListStore(bool, str, gobject.TYPE_PYOBJECT)
        self.watched_renderer = gtk.CellRendererToggle()
        self.watched_renderer.set_property('activatable', True)
        column = gtk.TreeViewColumn('Watched', self.watched_renderer)
        column.add_attribute(self.watched_renderer, "active", 0)
        self.append_column(column)
        episode_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Name', episode_renderer, text = 1)
        column.set_cell_data_func(episode_renderer,
                                  self._episode_select_view_data_func)
        self.append_column(column)
        self.set_model(model)
        self.get_model().set_sort_func(2, self._sort_func)
    
    def _sort_func(self, model, iter1, iter2):
        episode1 = model.get_value(iter1, self.EPISODE_OBJECT_COLUMN)
        episode2 = model.get_value(iter2, self.EPISODE_OBJECT_COLUMN)
        if episode1 == None or episode2 == None:
            return 0
        if episode1.episode_number < episode2.episode_number:
            return -1
        return 1

    def set_episodes(self, episode_list):
        model = self.get_model()
        model.clear()
        for episode in episode_list:
            name = str(episode)
            model.append([episode.watched, name, episode])

    def get_episode_from_path(self, path):
        model = self.get_model()
        iter = model.get_iter(path)
        episode = model.get_value(iter, self.EPISODE_OBJECT_COLUMN)
        return episode
    
    def sort_descending(self):
        self.get_model().set_sort_column_id(self.EPISODE_OBJECT_COLUMN,
                                            gtk.SORT_DESCENDING)
    
    def sort_ascending(self):
        self.get_model().set_sort_column_id(self.EPISODE_OBJECT_COLUMN,
                                            gtk.SORT_ASCENDING)
    
    def select_all(self):
        for path in self.get_model():
            path[0] = path[2].watched = True
    
    def select_none(self):
        for path in self.get_model() or []:
            path[self.EPISODE_CHECK_COLUMN] = \
                path[self.EPISODE_OBJECT_COLUMN].watched = False
    
    def _episode_select_view_data_func(self, column, renderer, model, iter):
        episode = model.get_value(iter, self.EPISODE_OBJECT_COLUMN)
        color = get_color(constants.SECONDARY_TEXT_COLOR)
        if not episode.watched and episode.already_aired():
            color = get_color(constants.DEFAULT_TEXT_COLOR)
        renderer.set_property('markup',
                              '<span foreground="%s">%s\n'
                              '%s</span>' % \
                              (color, episode, episode.get_air_date_text()))
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)

class EpisodeView(hildon.Window):
    
    def __init__(self, episode):
        super(EpisodeView, self).__init__()
        self.episode = episode
        
        self.set_title(str(self.episode))
        
        self.infotextview = InfoTextView()
        self._update_info_text_view()

        winscroll = gtk.ScrolledWindow()
        winscroll.add(self.infotextview)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.set_menu(self._create_menu())
        
        self.add(winscroll)
    
    def _update_info_text_view(self):
        self.infotextview.clear()
        self.infotextview.set_title(self.episode.name)
        self.infotextview.add_field(self.episode.overview)
        self.infotextview.add_field('\n')
        self.infotextview.add_field(self.episode.get_air_date_text(),
                                    _('Original air date'))
        self.infotextview.add_field(self.episode.director, _('Director'))
        self.infotextview.add_field(self.episode.writer, _('Writer'))
        self.infotextview.add_field(self.episode.guest_stars, _('Guest Stars'))
        self.infotextview.add_field(self.episode.rating, _('Rating'))
        self.set_title(self.episode.name)
    
    def _create_menu(self):
        menu = gtk.Menu()
        
        menuitem = gtk.MenuItem(_('Edit Info'))
        menuitem.connect('activate', self._edit_episode_cb)
        menu.append(menuitem)
        
        menu.show_all()
        return menu
    
    def _edit_episode_cb(self, button):
        edit_episode_dialog = EditEpisodeDialog(self,
                                               self.episode)
        response = edit_episode_dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            episode_info = edit_episode_dialog.get_info()
            self.episode.name = episode_info['name']
            self.episode.overview = episode_info['overview']
            self.episode.season_number = episode_info['season']
            self.episode.episode_number = episode_info['number']
            self.episode.air_date = episode_info['air_date']
            self.episode.director = episode_info['director']
            self.episode.writer = episode_info['writer']
            self.episode.rating = episode_info['rating']
            self.episode.guest_stars = episode_info['guest_stars']
            self._update_info_text_view()
        edit_episode_dialog.destroy()

class EpisodesSelectView(gtk.TreeView):
    
    def __init__(self):
        super(EpisodesSelectView, self).__init__()
        model = gtk.ListStore(str, gobject.TYPE_PYOBJECT)
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text = 0)
        self.append_column(column)
        self.set_model(model)

    def set_episodes(self, episode_list):
        model = self.get_model()
        model.clear()
        for episode in episode_list:
            name = str(episode)
            model.append([name, episode])

    def get_episode_from_path(self, path):
        model = self.get_model()
        iter = model.get_iter(path)
        episode = model.get_value(iter, 1)
        return episode

class InfoTextView(gtk.TextView):
    
    def __init__(self):
        super(InfoTextView, self).__init__()
        
        buffer = gtk.TextBuffer()
        self.iter = buffer.get_start_iter()

        self.set_buffer(buffer)
        self.set_wrap_mode(gtk.WRAP_WORD)
        self.set_editable(False)
        self.set_cursor_visible(False)
    
    def set_title(self, title):
        if not title:
            return
        title_tag = gtk.TextTag()
        title_tag.set_property('weight', pango.WEIGHT_BOLD)
        title_tag.set_property('size', pango.units_from_double(24.0))
        title_tag.set_property('underline-set', True)
        tag_table = self.get_buffer().get_tag_table()
        tag_table.add(title_tag)
        self.get_buffer().insert_with_tags(self.iter, str(title) + '\n', title_tag)
    
    def add_field(self, contents, label = None):
        if not contents:
            return
        if label:
            contents = _('\n%(label)s: %(contents)s') % {'label': label,
                                                         'contents': contents,
                                                        }
        self.get_buffer().insert(self.iter, contents)
    
    def clear(self):
        buffer = self.get_buffer()
        if not buffer:
            return
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())
        self.iter = buffer.get_start_iter()

class NewShowsDialog(gtk.Dialog):
    
    ADD_AUTOMATICALLY_RESPONSE = 1 << 0
    ADD_MANUALLY_RESPONSE      = 1 << 1
    
    def __init__(self):
        super(NewShowsDialog, self).__init__()
        self.set_title(_('Add Shows'))
        contents = gtk.HBox(True, 0)
        self.search_shows_button = gtk.Button()
        self.search_shows_button.set_label(_('Search Shows'))
        self.search_shows_button.connect('clicked', self._button_clicked_cb)        
        self.manual_add_button = gtk.Button()
        self.manual_add_button.set_label(_('Add Manually'))
        self.manual_add_button.connect('clicked', self._button_clicked_cb)
        contents.add(self.search_shows_button)
        contents.add(self.manual_add_button)
        self.vbox.add(contents)
        self.vbox.show_all()

    def _button_clicked_cb(self, button):
        if button == self.search_shows_button:
            self.response(self.ADD_AUTOMATICALLY_RESPONSE)
        elif button == self.manual_add_button:
            self.response(self.ADD_MANUALLY_RESPONSE)

class SearchShowsDialog(gtk.Dialog):
    
    def __init__(self, parent, series_manager):
        super(SearchShowsDialog, self).__init__(parent = parent,
                                                 buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                                            gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.set_title(_('Search shows'))
        
        self.series_manager = series_manager
        self.series_manager.connect('search-shows-complete', self._search_shows_complete_cb)
        
        self.connect('response', self._response_cb)
        
        self.chosen_show = None
        
        self.shows_view = gtk.TreeView()
        model = gtk.ListStore(str)
        self.shows_view.set_model(model)
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text = 0)
        self.shows_view.append_column(column)
        
        self.search_entry = gtk.Entry()
        self.search_entry.connect('changed', self._search_entry_changed_cb)
        self.search_button = gtk.Button()
        self.search_button.set_label(_('Search'))
        self.search_button.connect('clicked', self._search_button_clicked)
        self.search_button.set_sensitive(False)
        self.search_button.set_size_request(150, -1)
        search_contents = gtk.HBox(False, 0)
        search_contents.pack_start(self.search_entry, True, True, 0)
        search_contents.pack_start(self.search_button, False, False, 0)
        self.vbox.pack_start(search_contents, False, False, 0)
        
        winscroll = gtk.ScrolledWindow()
        winscroll.add(self.shows_view)
        winscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.vbox.add(winscroll)
        
        self.action_area.set_sensitive(False)
        
        self.vbox.show_all()
        self.set_size_request(-1, 400)
    
    def _search_entry_changed_cb(self, entry):
        enable = self.search_entry.get_text().strip()
        self.search_button.set_sensitive(bool(enable))
    
    def _search_button_clicked(self, button):
        self._set_controls_sensitive(False)
        self.progress = show_progress(self, _('Searching...'));
        search_terms = self.search_entry.get_text()
        if not self.search_entry.get_text():
            return
        self.series_manager.search_shows(search_terms)
    
    def _search_shows_complete_cb(self, series_manager, shows, error):
        if error:
            error_message = ''
            if 'socket' in str(error).lower():
                error_message = '\n ' + _('Please verify your internet connection '
                                          'is available')
                show_information(self, _('An error occurred.%s') % error_message)
        else:
            model = self.shows_view.get_model()
            if not model:
                return
            model.clear()
            if shows:
                for show in shows:
                    model.append([show])
                self.action_area.set_sensitive(True)
            else:
                self.action_area.set_sensitive(False)
        self.progress.destroy()
        self._set_controls_sensitive(True)
    
    def _set_controls_sensitive(self, sensitive):
        self.search_entry.set_sensitive(sensitive)
        self.search_button.set_sensitive(sensitive)
    
    def _response_cb(self, dialog, response):
        selection = self.shows_view.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            text = model.get_value(iter, 0)
            self.chosen_show = text

def show_information(parent, message):
    hildon.hildon_banner_show_information(parent,
                                          None,
                                          message)

def show_progress(parent, message):
    return hildon.hildon_banner_show_animation(parent,
                                               None,
                                               message)

def get_color(color_name):
    # Adapted from gPodder
    settings = gtk.settings_get_default()
    if not settings:
        return None
    color_style = gtk.rc_get_style_by_paths(settings,
                                            'GtkButton',
                                            'osso-logical-colors',
                                            gtk.Button)
    color = color_style.lookup_color(color_name)
    return "#%04x%04x%04x" % (color.red, color.green, color.blue)
