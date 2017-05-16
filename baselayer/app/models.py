from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.orm.exc import NoResultFound

from .json_util import to_json
from .custom_exceptions import AccessError


# The db has to be initialized later; this is done by the app itself
# See `app_server.py`
def init_db(user, database, password='', host='localhost', port=5432):
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, database)

    conn = sa.create_engine(url, client_encoding='utf8')

    DBSession.configure(bind=conn)
    Base.metadata.bind = conn

    return conn


DBSession = scoped_session(sessionmaker())


class BaseMixin(object):
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, nullable=False, default=datetime.now)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    __mapper_args__ = {'confirm_deleted_rows': False}

    def __str__(self):
        return to_json(self)

    def is_owned_by(self, user):
        if hasattr(self, 'users'):
            return (user in self.users)
        elif hasattr(self, 'project'):
            return (user in self.project.users)
        else:
            raise NotImplementedError(f"{type(self)} object has no owner")

    def to_dict(self):
        return {c.name: getattr(self, c.name)
                for c in type(self).__table__.columns}

    @classmethod
    def get_if_owned_by(cls, ident, user):
        try:
            obj = cls.query.get(ident)
        except NoResultFound:
            raise AccessError('No such feature set')

        if not obj.is_owned_by(user):
            raise AccessError('No such feature set')

        return obj


Base = declarative_base(cls=BaseMixin)


class User(Base):
    username = sa.Column(sa.String(), nullable=False, unique=True)
    email = sa.Column(sa.String(), nullable=False, unique=True)

    @classmethod
    def user_model(cls):
        return User

    def is_authenticated(self):
        return True

    def is_active(self):
        return True
