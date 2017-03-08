from zmq.eventloop import ioloop
ioloop.install()

from cesium_app import app_server
import tornado.log

# TODO: Capture --debug flag

app = app_server.make_app()
app.listen(65000)

ioloop.IOLoop.current().start()
