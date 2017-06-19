import time
from contextlib import contextmanager

from baselayer.app import models


@contextmanager
def status(message):
    print(f'[·] {message}', end='')
    try:
        yield
    except:
        print(f'\r[✗] {message}')
        raise
    else:
        print(f'\r[✓] {message}')


def drop_tables():
    conn = models.DBSession.session_factory.kw['bind']
    print(f'Dropping tables on database '
          f'"{str(conn.url).split(":")[1].strip("/")}"')
    models.Base.metadata.drop_all()


def create_tables(retry=5):
    """
    Create tables for all models, retrying 5 times at intervals of 3
    seconds if the database is not reachable.
    """
    for i in range(1, retry + 1):
        try:
            conn = models.DBSession.session_factory.kw['bind']
            print(f'Creating tables on database '
                  f'"{str(conn.url).split(":")[1].strip("/")}"')
            models.Base.metadata.create_all()

            print('Refreshed tables:')
            for m in models.Base.metadata.tables:
                print(f' - {m}')

            return

        except Exception as e:
            if (i == retry):
                raise e
            else:
                print('Could not connect to database...sleeping 3')
                time.sleep(3)


def clear_tables():
    drop_tables()
    create_tables()
