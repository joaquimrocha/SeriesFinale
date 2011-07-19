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
import logging
logging.basicConfig(level=logging.DEBUG)

class AsyncItem(object):

    def __init__(self, target_method, target_method_args, finish_callback = None, finish_callback_args = ()):
        self.target_method = target_method
        self.target_method_args = target_method_args
        self.finish_callback = finish_callback
        self.finish_callback_args = finish_callback_args
        self.canceled = False

    def run(self):
        if self.canceled:
            return
        results = error = None
        try:
            results = self.target_method(*self.target_method_args)
        except Exception, exception:
            logging.debug(str(exception))
            error = exception
        if self.canceled or not self.finish_callback:
            return
        self.finish_callback_args += (results,)
        self.finish_callback_args += (error,)
        self.finish_callback(*self.finish_callback_args) #TODO: Maybe some better way to do it like idle_add? QTimer::singleShot(0)?
        #gobject.idle_add(self.finish_callback, *self.finish_callback_args)

    def cancel(self):
        self.canceled = True

class AsyncWorker(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.queue = PriorityQueue()
        self.stopped = False
        self.async_item = None
        self.item_number = -1

    def run(self):
        while not self.stopped:
            if self.queue.empty():
                self.stop()
                break
            try:
                self.async_item = self.queue.get()
                self.item_number += 1
                self.async_item.run()
                self.async_item = None
            except Exception, exception:
                logging.debug(str(exception))
                self.stop()

    def stop(self):
        self.stopped = True
        if self.async_item:
            self.async_item.cancel()


class PriorityQueue(list):

    def __init__(self):
        list.__init__(self)

    def put(self, item):
        (item_priority, item_element) = item
        for i in range(0, len(self)):
            (last_priority, last_element) = self[i]
            if (last_priority > item_priority):
                self.insert(i, item)
                return
        self.append(item)

    def get(self):
        if self:
            value = self[0][1]
            del self[0]
            return value
        return None

    def empty(self):
        return not bool(self)
