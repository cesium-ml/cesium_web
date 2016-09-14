import tornado.web
import tornado.escape
import tornado.ioloop

from .. import models
from ..json_util import to_json
from ..flow import Flow


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.flow = Flow()

    def get_username(self):
        return "testuser@gmail.com"

    def push(action, payload={}):
        self.flow.push(self.get_username(), action, payload)

    def get_json(self):
        return tornado.escape.json_decode(self.request.body)

    def prepare(self):
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
                models.db.connect()
            except Exception as e:
                if (i == N):
                    raise e
                else:
                  print('Error connecting to database -- sleeping for a while')
                  time.sleep(5)

    def on_finish(self):
        models.db.close()

    def error(self, message):
        print('APP ERROR:', message)
        self.write({
            "status": "error",
            "message": message
            })

    def action(self, action, payload={}):
        self.flow.push(self.get_username(), action, payload)

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
