from .base import BaseHandler
from ..json_util import to_json

import tornado.web

import datetime
import jwt

# !!!
# This API call should **only be callable by logged in users**
# !!!

class SocketAuthTokenHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user is None:
            raise RuntimeError('No current user while authenticating socket. '
                               'This should NEVER happen.')

        secret = self.cfg['app:secret-key']
        token = jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            'username': self.current_user
            }, secret)
        self.success({'token': token})
