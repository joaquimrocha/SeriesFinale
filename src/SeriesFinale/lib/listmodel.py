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

from PySide import QtCore

class ListModel(QtCore.QAbstractListModel):
    def __init__(self, items = [], parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self._items = items
        self.setRoleNames({0: 'data'})

    def append(self, show):
        self.beginInsertRows(QtCore.QModelIndex(), len(self._items), len(self._items));
        self._items.append(show)
        self.endInsertRows()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._items)

    def data(self, index, role):
        if not index.isValid():
            return
        if role == 0:
            return self._items[index.row()]

    def list(self):
        return self._items

    def __len__(self):
        return self.rowCount()

    def __delitem__(self, index):
        self.beginRemoveRows(QtCore.QModelIndex(), index, index)
        del self._items[index]
        self.endRemoveRows()

    def __getitem__(self, key):
        return self._items[key]
