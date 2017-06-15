from baselayer.app.handlers.base import BaseHandler
from tornado.web import RequestHandler

class MainPageHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.render("login.html")
        else:
            self.render("index.html")
