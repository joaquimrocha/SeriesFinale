import hildon
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext
import locale
from series import SeriesManager

_ = gettext.gettext

gtk.gdk.threads_init()

class MainWindow(object):
    
    def __init__(self):
        self.window = hildon.StackableWindow()
        self.window.set_app_menu(self._create_menu())
        self.series_view = SeriesView(['Dexter', 'Sons of Anarchy'])
        self.series_manager = SeriesManager()
        area = hildon.PannableArea()
        area.add(self.series_view)
        self.window.add(area)
        
        self.series_manager.connect('get-full-show-complete', self._get_show_complete_cb)
    
    def _create_menu(self):
        menu = hildon.AppMenu()
        button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.set_label(_('Add Series'))
        button.connect('clicked', self._add_series_cb)
        menu.append(button)
        menu.show_all()
        return menu
    
    def _add_series_cb(self, button):
        new_series_dialog = NewSeriesDialog()
        response = new_series_dialog.run()
        new_series_dialog.destroy()
        if response == NewSeriesDialog.ADD_AUTOMATICALLY_RESPONSE:
            self._launch_search_series_dialog()
        elif response == NewSeriesDialog.ADD_MANUALLY_RESPONSE:
            print 'Add manually'
    
    def _launch_search_series_dialog(self):
        search_dialog = SearchSeriesDialog(self.series_manager)
        response = search_dialog.run()
        show = None
        if response == gtk.RESPONSE_ACCEPT:
            if search_dialog.chosen_show:
                hildon.hildon_gtk_window_set_progress_indicator(self.window, True)
                hildon.hildon_banner_show_information(self.window,
                                                      '',
                                                      _('Gathering show information. Please wait...'))
                self.series_manager.get_complete_show(search_dialog.chosen_show)
        search_dialog.destroy()
    
    def _get_show_complete_cb(self, series_manager, show):
        self.series_view.set_series([show.name])
        for ep in show.episode_list:
            print ep.name
        hildon.hildon_gtk_window_set_progress_indicator(self.window, False)

class SeriesView(gtk.TreeView):
    
    def __init__(self, series_list = []):
        super(SeriesView, self).__init__()
        self.series_list = series_list
        model = gtk.ListStore(str)
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text = 0)
        self.set_model(model)
        self.append_column(column)

    def set_series(self, series_list):
        model = self.get_model()
        model.clear()
        for series in series_list:
            model.append([series])
            print series

class NewSeriesDialog(gtk.Dialog):
    
    ADD_AUTOMATICALLY_RESPONSE = 1 << 0
    ADD_MANUALLY_RESPONSE      = 1 << 1
    
    def __init__(self):
        super(NewSeriesDialog, self).__init__()
        self.set_title(_('Add series'))
        contents = gtk.HBox(True, 0)
        self.search_series_button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.search_series_button.set_label(_('Search Series'))
        self.search_series_button.connect('clicked', self._button_clicked_cb)        
        self.manual_add_button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.manual_add_button.set_label(_('Add Manually'))
        self.search_series_button.connect('clicked', self._button_clicked_cb)
        contents.add(self.search_series_button)
        contents.add(self.manual_add_button)
        self.vbox.add(contents)
        self.vbox.show_all()

    def _button_clicked_cb(self, button):
        if button == self.search_series_button:
            self.response(self.ADD_AUTOMATICALLY_RESPONSE)
        elif button == self.manual_add_button:
            self.response(self.ADD_MANUALLY_RESPONSE)

class SearchSeriesDialog(gtk.Dialog):
    
    def __init__(self, series_manager):
        super(SearchSeriesDialog, self).__init__(buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.set_title(_('Search series'))
        
        self.series_manager = series_manager
        self.series_manager.connect('search-series-complete', self._search_series_complete_cb)
        
        self.connect('response', self._response_cb)
        
        self.chosen_show = None
        
        self.series_view = hildon.GtkTreeView(gtk.HILDON_UI_MODE_EDIT)
        model = gtk.ListStore(str)
        column = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text = 0)
        self.series_view.set_model(model)
        self.series_view.append_column(column)
        
        self.search_entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.search_button = hildon.GtkButton(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self.search_button.set_label(_('Search'))
        self.search_button.connect('clicked', self._search_button_clicked)
        search_contents = gtk.HBox(False, 0)
        search_contents.pack_start(self.search_entry, True, True, 0)
        search_contents.pack_start(self.search_button, False, False, 0)
        self.vbox.add(search_contents)
        
        series_area = hildon.PannableArea()
        series_area.add(self.series_view)
        series_area.set_size_request(-1, 250)
        self.vbox.add(series_area)
        
        self.vbox.show_all()
    
    def _search_button_clicked(self, button):
        self._set_controls_sensitive(False)
        hildon.hildon_gtk_window_set_progress_indicator(self, True)
        search_terms = self.search_entry.get_text()
        if not self.search_entry.get_text():
            return
        self.series_manager.search_series(search_terms)
    
    def _search_series_complete_cb(self, series_manager, series):
        hildon.hildon_gtk_window_set_progress_indicator(self, False)
        print series
        self.series_view.get_model().clear()
        for show in series:
            self.series_view.get_model().append([show])
        self._set_controls_sensitive(True)
    
    def _set_controls_sensitive(self, sensitive):
        self.search_button.set_sensitive(sensitive)
    
    def _response_cb(self, dialog, response):
        selection = self.series_view.get_selection()
        model, paths = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            text = model.get_value(iter, 0)
            self.chosen_show = text
                    

if __name__ == '__main__':
    main_window = MainWindow()
    main_window.window.show_all()
    gtk.main()