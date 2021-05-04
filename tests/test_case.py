import asyncio
import unittest

import gevent.monkey

import aiogevent


class TestCase(unittest.TestCase):
    def setUp(self):
        gevent.monkey.patch_all()
        policy = aiogevent.EventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        self.addCleanup(asyncio.set_event_loop_policy, None)
        self.loop = policy.get_event_loop()
        self.addCleanup(self.loop.close)
        self.addCleanup(asyncio.set_event_loop, None)
