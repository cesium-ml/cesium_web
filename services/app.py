from zmq.eventloop import ioloop
ioloop.install()

from cesium_app import app_server
import tornado.log
import argparse

parser = argparse.ArgumentParser(description='Launch webapp')
parser.add_argument('--config', action='append')
args = parser.parse_args()

app = app_server.make_app(args.config)
app.cfg.show()
app.listen(65000)

ioloop.IOLoop.current().start()
