from .base import BaseHandler


class MainPageHandler(BaseHandler):
    def get(self):
        return self.render("../../public/index.html", user=self.username)
