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

_ = gettext.gettext

gtk.gdk.threads_init()

class MainWindow(hildon.StackableWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.series_manager = SeriesManager()
        self.series_manager.load(constants.SF_CONF_FILE)
        self.series_manager.connect('show-list-changed',
                                    self._show_list_changed_cb)
        self.series_manager.connect('get-full-show-complete',
                                    self._get_show_complete_cb)

        self.shows_view = ShowsSelectView()
        self.shows_view.connect('row-activated', self._row_activated_cb)
        self.shows_view.set_shows(self.series_manager.series_list)
        self.set_title(constants.SF_NAME)
        self.set_app_menu(self._create_menu())
        area = hildon.PannableArea()
        area.add(self.shows_view)
        self.add(area)
        
        self.connect('delete-event', self._exit_cb)
        self._update_delete_menu_visibility()
    
    def _create_menu(self):
        menu = hildon.AppMenu()
        
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Add Shows'))
        button.connect('clicked', self._add_shows_cb)
        menu.append(button)
        
        self.delete_menu = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.delete_menu.set_label(_('Delete Shows'))
        self.delete_menu.connect('clicked', self._delete_shows_cb)
        menu.append(self.delete_menu)
        
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
        delete_shows_view = ShowsDeleteView(self.series_manager)
        delete_shows_view.shows_select_view.set_shows(self.series_manager.series_list)
        delete_shows_view.show_all()
    
    def _launch_search_shows_dialog(self):
        search_dialog = SearchShowsDialog(self, self.series_manager)
        response = search_dialog.run()
        show = None
        if response == gtk.RESPONSE_ACCEPT:
            if search_dialog.chosen_show:
                hildon.hildon_gtk_window_set_progress_indicator(self, True)
                show_information(self,
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
        hildon.hildon_gtk_window_set_progress_indicator(self, False)
    
    def _row_activated_cb(self, view, path, column):
        show = self.shows_view.get_show_from_path(path)
        seasons_view = SeasonsView(self.series_manager, show)
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
        self.series_manager.save(constants.SF_CONF_FILE)
        gtk.main_quit()

    def _show_list_changed_cb(self, series_manager):
        self.shows_view.set_shows(self.series_manager.series_list)
        self._update_delete_menu_visibility()
        return False
    
    def _update_delete_menu_visibility(self):
        if len(self.series_manager.series_list):
            self.delete_menu.show()
        else:
            self.delete_menu.hide()

class DeleteView(hildon.StackableWindow):
    
    def __init__(self,
                 tree_view,
                 toolbar_title = _('Delete'),
                 button_label = _('Delete')):
        super(DeleteView, self).__init__()
        self.tree_view = tree_view
        hildon.hildon_gtk_tree_view_set_ui_mode(self.tree_view, gtk.HILDON_UI_MODE_EDIT)
        self.tree_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        shows_area = hildon.PannableArea()
        shows_area.add(self.tree_view)
        self.add(shows_area)

        self.toolbar = hildon.EditToolbar()
        self.toolbar.set_label(toolbar_title)
        self.toolbar.set_button_label(button_label)
        self.toolbar.connect('arrow-clicked', lambda toolbar: self.destroy())
        self.set_edit_toolbar(self.toolbar)

        self.fullscreen()

class ShowsDeleteView(DeleteView):
    
    def __init__(self, series_manager):
        self.shows_select_view = ShowsSelectView()
        super(ShowsDeleteView, self).__init__(self.shows_select_view,
                                               _('Delete Series'),
                                               _('Delete'))
        self.series_manager = series_manager
        self.toolbar.connect('button-clicked',
                             self._button_clicked_cb)

    def _button_clicked_cb(self, button):
        selection = self.shows_select_view.get_selection()
        selected_rows = selection.get_selected_rows()
        model, paths = selected_rows
        if not paths:
            show_information(self, _('Please select one or more shows'))
            return
        for path in paths:
            self.series_manager.delete_show(model[path][1])
        self.destroy()

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
            show_info = '<small><span foreground="%s">' % constants.SECONDARY_TEXT_COLOR
            show_info += gettext.ngettext('%s season', '%s seasons', seasons) \
                         % seasons
            if show.is_completely_watched():
                show_info += ' | ' + _('Completely watched')
            else:
                episodes_to_watch = len([episode for episode in show.episode_list \
                                    if not episode.watched])
                if episodes_to_watch:
                    show_info += ' | ' + gettext.ngettext('%s episode not watched',
                                                          '%s episodes not watched',
                                                          episodes_to_watch) \
                                                          % episodes_to_watch
                else:
                    show_info += ' | ' + _('No episodes to watch')
            show_info += '</span></small>'
        else:
            show_info = ''
        renderer.set_property('markup',
                              '<b>%s</b>\n' % show.name +
                              show_info)
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)

class SeasonsView(hildon.StackableWindow):
    
    def __init__(self, series_manager, show):
        super(SeasonsView, self).__init__()
        self.set_title(show.name)
        
        self.series_manager = series_manager
        self.series_manager.connect('update-show-episodes-complete',
                                    self._update_show_episodes_complete_cb)
        self.show = show
        self.set_app_menu(self._create_menu())
        self.set_title(show.name)

        self.seasons_select_view = SeasonSelectView(self.show)
        seasons = self.show.get_seasons()
        self.seasons_select_view.set_seasons(seasons)
        self.seasons_select_view.connect('row-activated', self._row_activated_cb)
        
        seasons_area = hildon.PannableArea()
        seasons_area.add(self.seasons_select_view)
        self.add(seasons_area)
    
    def _row_activated_cb(self, view, path, column):
        season = self.seasons_select_view.get_season_from_path(path)
        episodes_view = EpisodesView(self.show, season)
        episodes_view.connect('delete-event', self._update_series_list_cb)
        episodes_view.connect('episode-list-changed', self._update_series_list_cb)
        episodes_view.show_all()
    
    def _update_series_list_cb(self, widget, event = None):
        seasons = self.show.get_seasons();
        self.seasons_select_view.set_seasons(seasons)
    
    def _create_menu(self):
        menu = hildon.AppMenu()
        
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Info'))
        button.connect('clicked', self._show_info_cb)
        menu.append(button)
        
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Edit Info'))
        button.connect('clicked', self._edit_show_info)
        menu.append(button)
        
        if str(self.show.thetvdb_id) != '-1':
            button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
            button.set_label(_('Update Show'))
            button.connect('clicked', self._update_series_cb)
            menu.append(button)
        
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('New Episode'))
        button.connect('clicked', self._new_episode_cb)
        menu.append(button)
        
        menu.show_all()
        return menu
    
    def _update_series_cb(self, button):
        self.series_manager.update_show_episodes(self.show)
        hildon.hildon_gtk_window_set_progress_indicator(self, True)
        self.set_sensitive(False)
        show_information(self, _('Updating show. Please wait...'))
    
    def _show_info_cb(self, button):
        dialog = gtk.Dialog(parent = self)
        dialog.set_title(_('Show Details'))
        infotextview = InfoTextView()
        infotextview.set_title(self.show.name)
        infotextview.add_field (self.show.overview)
        infotextview.add_field (_('\n'))
        infotextview.add_field (self.show.genre, _('Genre'))
        infotextview.add_field (self.show.network, _('Network'))
        infotextview.add_field (self.show.actors, _('Actors'))
        infotextview.add_field (self.show.rating, _('Rating'))
        info_area = hildon.PannableArea()
        info_area.add_with_viewport(infotextview)
        info_area.set_size_request_policy(hildon.SIZE_REQUEST_CHILDREN)
        dialog.vbox.add(info_area)
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
            episode.guest_stars = episode_info['guest_stars']
            self.show.update_episode_list([episode])
            seasons = self.show.get_seasons()
            self.seasons_select_view.set_seasons(seasons)
        new_episode_dialog.destroy()
    
    def _update_show_episodes_complete_cb(self, series_manager, show, error):
        if error:
            error_message = ''
            if 'socket' in str(error).lower():
                error_message = '\n ' + _('Please verify your internet connection '
                                          'is available')
            show_information((self, error_message))
        elif show == self.show:
            seasons = self.show.get_seasons()
            model = self.seasons_select_view.get_model()
            if model:
                model.clear()
                self.seasons_select_view.set_seasons(seasons)
        hildon.hildon_gtk_window_set_progress_indicator(self, False)
        self.set_sensitive(True)
    
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
        episodes = self.show.get_episode_list_by_season(season)
        episodes_to_watch = [episode for episode in episodes \
                            if not episode.watched]
        season_info = ''
        if not episodes_to_watch:
            if episodes:
                name = '<span foreground="%s">%s</span>' % \
                        (constants.SECONDARY_TEXT_COLOR, name)
                season_info = _('Completely watched')
        else:
            number_episodes_to_watch = len(episodes_to_watch)
            season_info = gettext.ngettext('%s episode not watched',
                                           '%s episodes not watched',
                                           number_episodes_to_watch) \
                                           % number_episodes_to_watch
            sorted_episodes_to_watch = [episode.episode_number for episode in \
                                        episodes_to_watch]
            sorted_episodes_to_watch.sort()
            next_episode = None
            for episode in episodes_to_watch:
                if episode.episode_number == sorted_episodes_to_watch[0]:
                    next_episode = episode
                    break
            season_info += ' | ' + _('<i>Next to watch:</i> %s') % episode
        renderer.set_property('markup',
                              '<b>%s</b>\n'
                              '<span foreground="%s">%s</span>' % \
                              (name, constants.SECONDARY_TEXT_COLOR, season_info))
        renderer.set_property('ellipsize', pango.ELLIPSIZE_END)

class NewShowDialog(gtk.Dialog):
    
    def __init__(self, parent):
        super(NewShowDialog, self).__init__(parent = parent,
                                             buttons = (gtk.STOCK_ADD,
                                                        gtk.RESPONSE_ACCEPT))
        
        self.set_title(_('Edit Show'))
        
        self.show_name = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.show_overview = hildon.TextView()
        self.show_overview.set_placeholder(_('Overview'))
        self.show_overview.set_wrap_mode(gtk.WRAP_WORD)
        self.show_genre = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.show_network = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.show_rating = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.show_actors = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        
        contents = gtk.VBox(False, 0)
        
        row = gtk.HBox(False, 12)
        row.pack_start(gtk.Label(_('Name:')), False, False, 0)
        row.pack_start(self.show_name, True, True, 0)
        contents.pack_start(row, False, False, 0)
        contents.pack_start(self.show_overview, False, False, 0)
        
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
        
        contents_area = hildon.PannableArea()
        contents_area.add_with_viewport(contents)
        contents_area.set_size_request_policy(hildon.SIZE_REQUEST_CHILDREN)
        
        self.vbox.add(contents_area)
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
                                               buttons = (gtk.STOCK_ADD,
                                                          gtk.RESPONSE_ACCEPT))
        
        self.set_title(_('New Episode'))
        
        self.episode_name = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_overview = hildon.TextView()
        self.episode_overview.set_placeholder(_('Overview'))
        self.episode_overview.set_wrap_mode(gtk.WRAP_WORD)
        
        self.episode_number = hildon.PickerButton(gtk.HILDON_SIZE_FINGER_HEIGHT,
                                                  hildon.BUTTON_ARRANGEMENT_VERTICAL)
        selector = hildon.TouchSelectorEntry(text = True)
        self.episode_number.set_title(_('Number:'))
        for i in xrange(20):
            selector.append_text(str(i + 1))
        self.episode_number.set_selector(selector)
        self.episode_number.set_active(0)
        
        self.episode_season = hildon.PickerButton(gtk.HILDON_SIZE_FINGER_HEIGHT,
                                                  hildon.BUTTON_ARRANGEMENT_VERTICAL)
        selector = hildon.TouchSelectorEntry(text = True)
        self.episode_season.set_title(_('Season:'))
        seasons = show.get_seasons()
        for season in seasons:
            selector.append_text(season)
        self.episode_season.set_selector(selector)
        if seasons:
            self.episode_season.set_active(len(seasons) - 1)
        else:
            selector.append_text('1')
            self.episode_season.set_active(0)
        
        self.episode_director = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_writer = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_rating = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.episode_guest_stars = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        
        contents = gtk.VBox(False, 0)
        
        row = gtk.HBox(False, 12)
        row.pack_start(gtk.Label(_('Name:')), False, False, 0)
        row.pack_start(self.episode_name, True, True, 0)
        contents.pack_start(row, False, False, 0)
        contents.pack_start(self.episode_overview, False, False, 0)
        row = gtk.HBox(False, 12)
        row.add(self.episode_season)
        row.add(self.episode_number)
        contents.pack_start(row, False, False, 0)
        
        fields = [(_('Director:'), self.episode_director),
                  (_('Writer:'), self.episode_writer),
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
        
        contents_area = hildon.PannableArea()
        contents_area.add_with_viewport(contents)
        contents_area.set_size_request_policy(hildon.SIZE_REQUEST_CHILDREN)
        
        self.vbox.add(contents_area)
        self.vbox.show_all()
    
    def get_info(self):
        buffer = self.episode_overview.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        overview_text = buffer.get_text(start_iter, end_iter)
        info = {'name': self.episode_name.get_text(),
                'overview': overview_text,
                'season': self.episode_season.get_selector().get_entry().get_text(),
                'number': self.episode_number.get_selector().get_entry().get_text(),
                'director': self.episode_director.get_text(),
                'writer': self.episode_writer.get_text(),
                'rating': self.episode_rating.get_text(),
                'guest_stars': self.episode_guest_stars.get_text()}
        return info

class EditEpisodeDialog(NewEpisodeDialog):
    
    def __init__(self, parent, episode):
        super(EditEpisodeDialog, self).__init__(parent, episode.show)
        
        self.episode_name.set_text(episode.name)
        self.episode_overview.get_buffer().set_text(episode.overview)
        self.episode_season.get_selector().get_entry().set_text(episode.season_number)
        self.episode_number.get_selector().get_entry().set_text(str(episode.episode_number))
        self.episode_director.set_text(episode.director)
        self.episode_writer.set_text(str(episode.writer))
        self.episode_rating.set_text(episode.rating)
        self.episode_guest_stars.set_text(str(episode.guest_stars))

class EpisodesView(hildon.StackableWindow):
    
    EPISODES_LIST_CHANGED_SIGNAL = 'episode-list-changed'
    
    __gsignals__ = {EPISODES_LIST_CHANGED_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                                   gobject.TYPE_NONE,
                                                   ()),
                   }
    
    def __init__(self, show, season_number = None):
        super(EpisodesView, self).__init__()
        
        self.show = show
        self.season_number = season_number
        self.set_title(self.show.name)
        self.episodes_check_view = EpisodesCheckView()
        self.episodes_check_view.set_episodes(self.show.get_episodes_by_season(self.season_number))
        self.episodes_check_view.watched_renderer.connect('toggled',
                                                          self._watched_renderer_toggled_cb,
                                                          self.episodes_check_view.get_model())
        self.episodes_check_view.connect('row-activated', self._row_activated_cb)
        
        episodes_area = hildon.PannableArea()
        episodes_area.add(self.episodes_check_view)
        self.add(episodes_area)
        self.set_app_menu(self._create_menu())
        self._sort_descending_cb(None)
    
    def _create_menu(self):
        menu = hildon.AppMenu()
        
        button = hildon.GtkRadioButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_mode(False)
        button.set_label(_('A-Z'))
        button.connect('clicked', self._sort_ascending_cb)
        menu.add_filter(button)
        button = hildon.GtkRadioButton(gtk.HILDON_SIZE_FINGER_HEIGHT, group = button)
        button.set_active(True)
        button.set_mode(False)
        button.set_label(_('Z-A'))
        button.connect('clicked', self._sort_descending_cb)
        menu.add_filter(button)
        
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Mark All'))
        button.connect('clicked', self._select_all_cb)
        menu.append(button)
        
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Mark None'))
        button.connect('clicked', self._select_none_cb)
        menu.append(button)

        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Delete Episodes'))
        button.connect('clicked', self._delete_episodes_cb)
        menu.append(button)

        menu.show_all()
        return menu
    
    def _delete_episodes_cb(self, button):
        delete_episodes_view = EpisodesDeleteView(self.show)
        episodes = self.show.get_episodes_by_season(self.season_number)
        delete_episodes_view.episodes_select_view.set_episodes(episodes)
        delete_episodes_view.toolbar.connect('button-clicked',
                                             self._update_episodes_list_cb)
        delete_episodes_view.show_all()
    
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
    
    def _sort_descending_cb(self, button):
        self.episodes_check_view.sort_descending()

class EpisodesCheckView(gtk.TreeView):
    
    def __init__(self):
        super(EpisodesCheckView, self).__init__()
        model = gtk.ListStore(bool, str, gobject.TYPE_PYOBJECT)
        self.watched_renderer = gtk.CellRendererToggle()
        self.watched_renderer.set_property('activatable', True)
        column = gtk.TreeViewColumn('Watched', self.watched_renderer)
        column.add_attribute(self.watched_renderer, "active", 0)
        self.append_column(column)
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text = 1)
        self.append_column(column)
        self.set_model(model)
        self.get_model().set_sort_func(2, self._sort_func)
    
    def _sort_func(self, model, iter1, iter2):
        episode1 = model.get_value(iter1, 2)
        episode2 = model.get_value(iter2, 2)
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
        episode = model.get_value(iter, 2)
        return episode
    
    def sort_descending(self):
        self.get_model().set_sort_column_id(2, gtk.SORT_DESCENDING)
    
    def sort_ascending(self):
        self.get_model().set_sort_column_id(2, gtk.SORT_ASCENDING)
    
    def select_all(self):
        for path in self.get_model():
            path[0] = path[2].watched = True
    
    def select_none(self):
        for path in self.get_model() or []:
            path[0] = path[2].watched = False

class EpisodeView(hildon.StackableWindow):
    
    def __init__(self, episode):
        super(EpisodeView, self).__init__()
        self.episode = episode
        
        self.set_title(str(self.episode))
        
        contents_area = hildon.PannableArea()
        contents = gtk.VBox(False, 0)
        contents_area.add_with_viewport(contents)
        
        self.infotextview = InfoTextView()
        self._update_info_text_view()
        contents.add(self.infotextview)
        
        self.set_app_menu(self._create_menu())
        
        self.add(contents_area)
    
    def _update_info_text_view(self):
        self.infotextview.clear()
        self.infotextview.set_title(self.episode.name)
        self.infotextview.add_field(self.episode.overview)
        self.infotextview.add_field('\n')
        self.infotextview.add_field(self.episode.director, _('Director'))
        self.infotextview.add_field(self.episode.writer, _('Writer'))
        self.infotextview.add_field(self.episode.guest_stars, _('Guest Stars'))
        self.infotextview.add_field(self.episode.rating, _('Rating'))
        self.set_title(self.episode.name)
    
    def _create_menu(self):
        menu = hildon.AppMenu()
        
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Edit Info'))
        button.connect('clicked', self._edit_episode_cb)
        menu.append(button)
        
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
            self.episode.director = episode_info['director']
            self.episode.writer = episode_info['writer']
            self.episode.rating = episode_info['rating']
            self.episode.guest_stars = episode_info['guest_stars']
            self._update_info_text_view()
        edit_episode_dialog.destroy()

class EpisodesDeleteView(DeleteView):
    
    def __init__(self, show):
        self.episodes_select_view = EpisodesSelectView()
        super(EpisodesDeleteView, self).__init__(self.episodes_select_view,
                                                 _('Delete Episodes'),
                                                 _('Delete'))
        self.show = show
        self.toolbar.connect('button-clicked',
                             self._button_clicked_cb)

    def _button_clicked_cb(self, button):
        selection = self.episodes_select_view.get_selection()
        selected_rows = selection.get_selected_rows()
        model, paths = selected_rows
        if not paths:
            show_information(self, _('Please select one or more episodes'))
            return
        for path in paths:
            self.show.delete_episode(model[path][1])
        self.destroy()

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

class InfoTextView(hildon.TextView):
    
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
            contents = _('\n%s: %s') % (label, contents)
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
        self.search_shows_button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.search_shows_button.set_label(_('Search Series'))
        self.search_shows_button.connect('clicked', self._button_clicked_cb)        
        self.manual_add_button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
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
                                                 buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.set_title(_('Search shows'))
        
        self.series_manager = series_manager
        self.series_manager.connect('search-shows-complete', self._search_shows_complete_cb)
        
        self.connect('response', self._response_cb)
        
        self.chosen_show = None
        
        self.shows_view = hildon.GtkTreeView(gtk.HILDON_UI_MODE_EDIT)
        model = gtk.ListStore(str)
        self.shows_view.set_model(model)
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text = 0)
        self.shows_view.append_column(column)
        
        self.search_entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.search_entry.connect('changed', self._search_entry_changed_cb)
        self.search_button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.search_button.set_label(_('Search'))
        self.search_button.connect('clicked', self._search_button_clicked)
        self.search_button.set_sensitive(False)
        self.search_button.set_size_request(150, -1)
        search_contents = gtk.HBox(False, 0)
        search_contents.pack_start(self.search_entry, True, True, 0)
        search_contents.pack_start(self.search_button, False, False, 0)
        self.vbox.pack_start(search_contents, False, False, 0)
        
        shows_area = hildon.PannableArea()
        shows_area.add(self.shows_view)
        shows_area.set_size_request_policy(hildon.SIZE_REQUEST_CHILDREN)
        self.vbox.add(shows_area)
        
        self.action_area.set_sensitive(False)
        
        self.vbox.show_all()
        self.set_size_request(-1, 400)
    
    def _search_entry_changed_cb(self, entry):
        enable = self.search_entry.get_text().strip()
        self.search_button.set_sensitive(bool(enable))
    
    def _search_button_clicked(self, button):
        self._set_controls_sensitive(False)
        hildon.hildon_gtk_window_set_progress_indicator(self, True)
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
        hildon.hildon_gtk_window_set_progress_indicator(self, False)
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
                                          '',
                                          message)
