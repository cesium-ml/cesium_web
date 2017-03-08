from .base import BaseHandler


class MainPageHandler(BaseHandler):
    def get(self):
        #self.render("index.html", user=self.username)
        #print('rendered')
        self.render("index.html", user=self.username)
