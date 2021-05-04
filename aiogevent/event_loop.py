import asyncio

import gevent

from .selector import _Selector


class EventLoop(asyncio.SelectorEventLoop):
    def __init__(self):
        self._greenlet = None
        selector = _Selector(self)
        super(EventLoop, self).__init__(selector=selector)
        self.set_debug(True)
        print(self.__dict__)

    def time(self):
        return gevent.core.time()

    def call_soon(self, callback, *args, **kwargs):
        handle = super(EventLoop, self).call_soon(callback, *args, **kwargs)
        if self._selector is not None and self._selector._event:
            # selector.select() is running: write into the self-pipe to wake up
            # the selector
            self._write_to_self()
        return handle

    def call_at(self, when, callback, *args, **kwargs):
        handle = super(EventLoop, self).call_at(when, callback, *args, **kwargs)
        if self._selector is not None and self._selector._event:
            # selector.select() is running: write into the self-pipe to wake up
            # the selector
            self._write_to_self()
        return handle

    def run_forever(self):
        self._greenlet = gevent.getcurrent()
        print(self._greenlet)
        try:
            super(EventLoop, self).run_forever()
        finally:
            self._greenlet = None
    
    def stop(self):
        super().stop()

