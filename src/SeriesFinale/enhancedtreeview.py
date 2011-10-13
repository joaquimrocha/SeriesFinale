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

import gtk, gobject

class EnhancedTreeView(gtk.TreeView):

    LONG_PRESS_SIGNAL = 'long-press'
    LONG_PRESS_MOTION_THRESHOLD = 25
    LONG_PRESS_TIMEOUT = 500

    __gsignals__ = {LONG_PRESS_SIGNAL: (gobject.SIGNAL_RUN_LAST,
                                        gobject.TYPE_NONE,
                                        (gobject.TYPE_PYOBJECT,
                                         gobject.TYPE_PYOBJECT)),
                   }

    def __init__(self):
        super(EnhancedTreeView, self).__init__()
        self._initial_press_x = -1
        self._initial_press_y = -1
        self._press_timeout = 0
        self._long_pressed = False

    def do_button_press_event(self, event):
        self._initial_press_x = event.x
        self._initial_press_y = event.y
        self._press_timeout = gobject.timeout_add(self.LONG_PRESS_TIMEOUT,
                                                  self._press_timeout_cb)
        return gtk.TreeView.do_button_press_event(self, event)

    def do_button_release_event(self, event):
        if self._press_timeout:
            gobject.source_remove(self._press_timeout)
            self._press_timeout = 0
            self._initial_press_x = self._initial_press_y = 0
        if self._long_pressed:
            self._long_pressed = False
            event.x = event.y = -1.0
        return gtk.TreeView.do_button_release_event(self, event)

    def do_motion_notify_event(self, event):
        if abs(event.x - self._initial_press_x) > self.LONG_PRESS_MOTION_THRESHOLD or \
           abs(event.y - self._initial_press_y) > self.LONG_PRESS_MOTION_THRESHOLD:
            if self._press_timeout:
                gobject.source_remove(self._press_timeout)
            self._press_timeout = 0
            self._initial_press_x = self._initial_press_y = 0
        return gtk.TreeView.do_motion_notify_event(self, event)

    def _press_timeout_cb(self):
        self._long_pressed = True
        path = self.get_path_at_pos(int(self._initial_press_x),
                                    int(self._initial_press_y))
        gtk.gdk.threads_enter()
        self.emit(self.LONG_PRESS_SIGNAL, path[0], path[1])
        gtk.gdk.threads_leave()
        self._initial_press_x = self._initial_press_y = 0
        return False

gobject.type_register(EnhancedTreeView)
