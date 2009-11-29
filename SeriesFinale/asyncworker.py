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

from threading import Thread
import gobject
import glib

class AsyncWorker(Thread):
    
    def __init__(self, target_method, target_method_args, finish_callback, finish_callback_args = ()):
        Thread.__init__(self)
        self.stopped = False
        self.target_method = target_method
        self.target_method_args = target_method_args
        self.finish_callback = finish_callback
        self.finish_callback_args = finish_callback_args

    def run(self):
        ret = error = None
        if self.target_method != None:
            try:
                ret = self.target_method(self.target_method_args)
            except Exception, exception:
                error = exception
        if self.finish_callback != None and not self.stopped:
            self.finish_callback_args += (ret, error)
            gobject.idle_add(self.finish_callback, *self.finish_callback_args)
