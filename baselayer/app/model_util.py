import inspect
import textwrap
import time
import peewee as pw
from contextlib import contextmanager

from . import models
from . import psa
from .json_util import to_json


@contextmanager
def status(message):
    print('[·] {}'.format(message), end='')
    try:
        yield
    except:
        print('\r[✗] {}'.format(message))
        raise
    else:
        print('\r[✓] {}'.format(message))


def filter_pw_models(members):
    return [obj for (name, obj) in members
                if inspect.isclass(obj) and issubclass(obj, pw.Model)
                and not obj == models.BaseModel]


app_models = filter_pw_models(inspect.getmembers(models))
psa_models = filter_pw_models(inspect.getmembers(psa))
all_models = app_models + psa_models


def drop_tables(models_to_drop=all_models):
    print('Dropping tables on database "{}"'.format(models.db.database))
    models.db.drop_tables(models_to_drop, safe=True, cascade=True)


def create_tables(models_to_create=all_models, retry=5):
    """
    Create tables for all models, retrying 5 times at intervals of 3
    seconds if the database is not reachable.
    """
    for i in range(1, retry + 1):
        try:
            print('Refreshing tables on db "{}"'.format(models.db.database))
            models.db.create_tables(models_to_create, safe=True)

            print('Refreshed tables:')
            for m in models_to_create:
                print(' - {}'.format(m.__name__))

            return

        except Exception as e:
            if (i == retry):
                raise e
            else:
                print('Could not connect to database...sleeping 5')
                time.sleep(3)


def clear_tables(models_to_clear=all_models):
    drop_tables(models_to_clear)
    create_tables(models_to_clear)
