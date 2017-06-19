import tornado.escape
import tornado.ioloop
from sqlalchemy.orm.exc import NoResultFound

# The Python Social Auth base handler gives us:
#   user_id, get_current_user, login_user
#
# `get_current_user` is needed by tornado.authentication,
# and provides a cached version, `current_user`, that should
# be used to look up the logged in user.
from social_tornado.handlers import BaseHandler as PSABaseHandler

from ..models import DBSession, User
from ..json_util import to_json
from ..flow import Flow

import time


class BaseHandler(PSABaseHandler):
    def prepare(self):
        self._baselayer_cfg = self.application._baselayer_cfg
        self.cfg = self.application.cfg
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
                assert DBSession.session_factory.kw['bind'] is not None
            except Exception as e:
                if (i == N):
                    raise e
                else:
                    print('Error connecting to database, sleeping for a while')
                    time.sleep(5)

        return super(BaseHandler, self).prepare()

    def get_current_user(self):
        if not self._baselayer_cfg['server:multi_user']:
            username = 'testuser@gmail.com'
            try:
                return User.query.filter(User.username == username).one()
            except NoResultFound:
                u = User(username=username, email=username)
                DBSession.add(u)
                DBSession().commit()
                return u
        else:
            user_id = self.get_secure_cookie('user_id')
            if user_id is None:
                return None
            else:
                return User.query.get(int(user_id))

    def push(self, action, payload={}):
        self.flow.push(self.current_user.username, action, payload)

    def get_json(self):
        return tornado.escape.json_decode(self.request.body)

    def on_finish(self):
        DBSession.remove()
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

    async def _get_client(self):
        IP = '127.0.0.1'
        PORT = 63000
        PORT_SCHEDULER = 63500

        from distributed import Client
        client = await Client('{}:{}'.format(IP, PORT_SCHEDULER),
                              asynchronous=True)

        return client
