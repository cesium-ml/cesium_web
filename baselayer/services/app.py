import importlib
import argparse

from zmq.eventloop import ioloop

from baselayer.app import cfg
from baselayer.app.app_server import handlers, settings

import tornado.log

ioloop.install()

parser = argparse.ArgumentParser(description='Launch webapp')
parser.add_argument('--config', action='append')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

app_factory = cfg['app:factory']

module, app_factory = app_factory.rsplit('.', 1)
app_factory = getattr(importlib.import_module(module), app_factory)


app = app_factory(args.config, debug=args.debug)
app._baselayer_cfg = cfg
app.cfg = cfg

app.listen(cfg['app:port'])

ioloop.IOLoop.current().start()
