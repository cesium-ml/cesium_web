"""
Python Social Auth: storage and user model definitions

https://github.com/python-social-auth
"""

from social_sqlalchemy.storage import (SQLAlchemyUserMixin,
                                       SQLAlchemyAssociationMixin,
                                       SQLAlchemyNonceMixin,
                                       SQLAlchemyCodeMixin,
                                       SQLAlchemyPartialMixin,
                                       BaseSQLAlchemyStorage)
from social_tornado.models import TornadoStorage
from social_core.backends.google import GoogleOAuth2

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .models import Base, User, DBSession


class UserSocialAuth(Base, SQLAlchemyUserMixin):
    """
    This model is used by PSA to store whatever it needs during
    authentication, e.g. token expiration time, etc.
    """
    uid = sa.Column(sa.String())
    user_id = sa.Column(sa.ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', backref='social_auth')

    def username_max_length():
        return 255

    @classmethod
    def _session(cls):
        return DBSession()

    @classmethod
    def user_model(cls):
        return User


class FakeGoogleOAuth2(GoogleOAuth2):
    AUTHORIZATION_URL = 'http://localhost:63000/fakeoauth2/auth'
    ACCESS_TOKEN_URL = 'http://localhost:63000/fakeoauth2/token'

    def user_data(self, access_token, *args, **kwargs):
        return {
            'id': 'testuser@gmail.com',
            'emails': [{'value': 'testuser@gmail.com', 'type': 'home'}]
        }
