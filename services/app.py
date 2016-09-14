from cesium_app import app_server
import tornado.ioloop

# TODO: Capture --debug flag

app = app_server.make_app()
app.listen(65000)
tornado.ioloop.IOLoop.current().start()
