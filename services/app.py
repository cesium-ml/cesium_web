from cesium_app import app_server
import tornado.ioloop
import tornado.log

# TODO: Capture --debug flag

tornado.log.enable_pretty_logging()

app = app_server.make_app()
app.listen(65000)

tornado.ioloop.IOLoop.current().start()

