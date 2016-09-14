from .base import BaseHandler
from ..config import cfg
from ..json_util import to_json

import datetime
import jwt

# !!!
# This API call should **only be callable by logged in users**
# !!!

class SocketAuthTokenHandler(BaseHandler):
    def get(self):
        secret = cfg['app']['secret-key']
        token = jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            'username': self.get_username()
            }, secret)
        self.success({'token': token})
