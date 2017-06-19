import tornado.web


class AccessError(tornado.web.HTTPError):
    def __init__(self, reason, status_code=400):
        tornado.web.HTTPError.__init__(self, reason=reason,
                                       status_code=400)

    def __str__(self):
        return self.reason
