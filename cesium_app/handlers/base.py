import tornado.web
import tornado.escape
import tornado.ioloop

# The Python Social Auth base handler gives us:
#   user_id, get_current_user, login_user
#
# `get_current_user` is needed by tornado.authentication,
# and provides a cached version, `current_user`, that should
# be used to look up the logged in user.
from social_tornado.handlers import BaseHandler as PSABaseHandler

from .. import models
from ..json_util import to_json
from ..flow import Flow

import time


class BaseHandler(PSABaseHandler):
    def prepare(self):
        self.flow = Flow()

        # Remove slash prefixes from arguments
        if self.path_args and self.path_args[0] is not None:
            self.path_args = [arg.lstrip('/') for arg in self.path_args]
            self.path_args = [arg if (arg != '') else None
                                  for arg in self.path_args]

        # If there are no arguments, make it explicit, otherwise
        # get / post / put / delete all have to accept an optional kwd argument
        if len(self.path_args) == 1 and self.path_args[0] is None:
            self.path_args = []

        # TODO Refactor to be a context manager or utility function
        N = 5
        for i in range(1, N + 1):
            try:
                if models.db.is_closed():
                    models.db.connect()
            except Exception as e:
                if (i == N):
                    raise e
                else:
                    print('Error connecting to database -- sleeping for a while')
                    time.sleep(5)

        return super(BaseHandler, self).prepare()

    def get_current_user(self):
        user_id = self.get_secure_cookie('user_id')
        if user_id is None:
            return None
        else:
            try:
                return models.User.get(id=int(user_id))
            except models.User.DoesNotExist:
                return None

    def push(self, action, payload={}):
        self.flow.push(self.current_user.username, action, payload)

    def get_json(self):
        return tornado.escape.json_decode(self.request.body)

    def on_finish(self):
        if not models.db.is_closed():
            models.db.close()

        return super(BaseHandler, self).on_finish()

    def error(self, message):
        print('! App Error:', message)

        self.set_status(200)
        self.write({
            "status": "error",
            "message": message
            })

    def action(self, action, payload={}):
        self.push(action, payload)

    def success(self, data={}, action=None, payload={}):
        if action is not None:
            self.action(action, payload)

        self.write(to_json(
            {
                "status": "success",
                "data": data
            }))

    def write_error(self, status_code, exc_info=None):
        if exc_info is not None:
            err_cls, err, traceback = exc_info
        else:
            err = 'An unknown error occurred'

        self.error(str(err))

    @tornado.gen.coroutine
    def _get_executor(self):
        loop = tornado.ioloop.IOLoop.current()

        IP = '127.0.0.1'
        PORT = 63000
        PORT_SCHEDULER = 63500

        from distributed import Executor
        executor = Executor('{}:{}'.format(IP, PORT_SCHEDULER), loop=loop,
                            start=False)
        yield executor._start()

        return executor


class AccessError(tornado.web.HTTPError):
    def __init__(self, reason, status_code=400):
        tornado.web.HTTPError.__init__(self, reason=reason,
                                       status_code=400)

    def __str__(self):
        return self.reason
