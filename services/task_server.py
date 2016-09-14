# encoding: utf-8

import tornado.web
import tornado.ioloop
import tornado.gen

import json
import requests
import traceback
from cesium_app.config import cfg


IP = '127.0.0.1'
PORT_SCHEDULER = 63500


if __name__ == "__main__":
    loop = tornado.ioloop.IOLoop.current()

    from distributed import Scheduler
    s = Scheduler(loop=loop)
    s.start(PORT_SCHEDULER)
    print('Task scheduler listening on port {}'.format(PORT_SCHEDULER))

    from distributed import Worker
    w = Worker('127.0.0.1', PORT_SCHEDULER, loop=loop, ncores=1)
    w.start(0)
    print('Single worker activated')

    print('Starting main loop...')
    loop.start()
