from threading import Thread
import gobject

class AsyncWorker(Thread):
    
    def __init__(self, target_method, target_method_args, finish_callback):
        Thread.__init__(self)
        self.stopped = False
        self.target_method = target_method
        self.target_method_args = target_method_args
        self.finish_callback = finish_callback

    def run(self):
        ret = None
        if self.target_method != None:
            ret = self.target_method(self.target_method_args)
        if self.finish_callback != None and not self.stopped:
            gobject.idle_add(self.finish_callback, ret)
