"""
Python Social Auth: storage and user model definitions

https://github.com/python-social-auth
"""

from social_peewee.storage import (
    database_proxy, BasePeeweeStorage,
    PeeweeAssociationMixin, PeeweeCodeMixin,
    PeeweeNonceMixin, PeeweePartialMixin, PeeweeUserMixin
)

from social_core.backends.google import GoogleOAuth2

import peewee as pw
from .models import BaseModel, User, db


database_proxy.initialize(db)


class UserSocialAuth(BaseModel, PeeweeUserMixin):
    """
    This model is used by PSA to store whatever it needs during
    authentication, e.g. token expiration time, etc.
    """
    user = pw.ForeignKeyField(User, related_name='social_auth')

    @classmethod
    def user_model(cls):
        return User


class TornadoPeeweeStorage(BasePeeweeStorage):
    """
    Storage definition for Peewee + Tornado.

    We use PSA's default Peewee implementation.

    http://python-social-auth.readthedocs.io/en/latest/storage.html#storage-interface
    """

    class nonce(PeeweeNonceMixin):
        """Single use numbers"""
        pass

    class association(PeeweeAssociationMixin):
        """OpenId account association"""
        pass

    class code(PeeweeCodeMixin):
        """Mail validation single one time use code"""
        pass

    class partial(PeeweePartialMixin):
        pass

    user = UserSocialAuth


class FakeGoogleOAuth2(GoogleOAuth2):
    AUTHORIZATION_URL = 'http://localhost:63000/fakeoauth2/auth'
    ACCESS_TOKEN_URL = 'http://localhost:63000/fakeoauth2/token'

    def user_data(self, access_token, *args, **kwargs):
        return {
            'id': 'testuser@gmail.com',
            'emails': [{'value': 'testuser@gmail.com', 'type': 'home'}]
        }
