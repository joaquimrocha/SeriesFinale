#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
#    Copyright (C) 2010 Sergio Villar Senin <svillar@igalia.com>
#
#    This file is part of ReSiStance
#
#    ReSiStance is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    ReSiStance is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with ReSiStance.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import conic
import gobject, dbus
from dbus.mainloop.glib import DBusGMainLoop

class ConnectionManager(gobject.GObject):
    __gsignals__ = {
        "connection-changed": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
        }

    _INITIAL_STATUS = -1

    def __init__(self):

        super(ConnectionManager, self).__init__()

        # Get a connection to the bus. Force a connection request in
        # order to know the current status
        self._iap_id = None
        self._status = self._INITIAL_STATUS

        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        self._connection = conic.Connection()
        self._connection.set_property("automatic-connection-events", True)
        self._connection.connect("connection-event", self._connection_cb)
        self._connection.request_connection(conic.CONNECT_FLAG_AUTOMATICALLY_TRIGGERED)

    def _connection_cb(self, connection, event, data=None):
        notify = False
        status = event.get_status()
        error = event.get_error()
        iap_id = event.get_iap_id()
        bearer = event.get_bearer_type()

        if status == conic.STATUS_CONNECTED:
            if self._status == conic.STATUS_CONNECTED:
                if self._iap_id != iap_id:
                    # Reconnection to a different network
                    self._iap_id = iap_id
                    notify = True
            else:
                # New connection
                self._status = conic.STATUS_CONNECTED
                self._iap_id = iap_id
                notify = True
        elif status == conic.STATUS_DISCONNECTING:
            if self._iap_id == iap_id:
                # Just change the status. We do not notify but the
                # status prevents new network operations
                self._status = status
            else:
                # Some other connection is disconnecting
                pass
        else:
            assert(status == conic.STATUS_DISCONNECTED)
            if self._iap_id == iap_id:
                # Current connection was disconnected
                self._iap_id = None
                self._status = status
                notify = True
            else:
                # Some other connection was disconnected
                pass

        if notify:
            self.emit('connection-changed')

    def is_online(self):
        return self._status == conic.STATUS_CONNECTED
