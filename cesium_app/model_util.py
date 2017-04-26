import inspect
import textwrap
import peewee as pw
from contextlib import contextmanager

from cesium_app import models, psa
from cesium_app.json_util import to_json


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


def _filter_pw_models(members):
    return [obj for (name, obj) in members
                if inspect.isclass(obj) and issubclass(obj, pw.Model)
                and not obj == models.BaseModel]


app_models = _filter_pw_models(inspect.getmembers(models))
psa_models = _filter_pw_models(inspect.getmembers(psa))
all_models = app_models + psa_models


def drop_tables():
    print('Dropping tables on database "{}"'.format(models.db.database))
    models.db.drop_tables(all_models, safe=True, cascade=True)


def create_tables(retry=5):
    """
    Create tables for all models, retrying 5 times at intervals of 3
    seconds if the database is not reachable.
    """
    for i in range(1, retry + 1):
        try:
            print('Creating tables on db "{}"'.format(models.db.database))
            models.db.create_tables(all_models, safe=True)

            print('Created tables:')
            for m in all_models:
                print(' - {}'.format(m.__name__))

            return

        except Exception as e:
            if (i == retry):
                raise e
            else:
                print('Could not connect to database...sleeping 5')
                time.sleep(3)


def clear_tables():
    drop_tables()
    create_tables()


def insert_test_data():
    with status("Dropping all tables"):
        drop_tables()

    with status("Creating tables"):
        create_tables()

    for model in all_models:
        print('    -', model.__name__)

    USERNAME = 'testuser@gmail.com'
    with status("Creating dummy user: {}... ".format(USERNAME)):
        u = models.User.create(username=USERNAME, email=USERNAME)

    for i in range(5):
        with status("Inserting dummy project"):
            p = models.Project.create(name='test project {}'.format(i))

        print('\n{}\n'.format(textwrap.indent(str(p), '  ')))

    with status("Assign project owner... "):
        for i in range(3):
            p = models.Project.get(models.Project.id == i + 1)
            up = models.UserProject.create(user=u, project=p)

    with status("Assert that user has 3 projects"):
        assert(len(list(p.all('testuser@gmail.com'))) == 3)

    with status("Inserting dummy dataset and time series... "):
        file_uris = ['/dir/ts{}.npz'.format(i) for i in range(3)]
        d = models.Dataset.add(name='test dataset', project=p, file_uris=file_uris)

    with status("Inserting dummy featureset... "):
        test_file = models.File.get()
        f = models.Featureset.create(project=p, dataset=d, name='test featureset',
                              features_list=['amplitude'], file=test_file)

    with status("Inserting dummy model... "):
        m = models.Model.create(project=p, featureset=f, name='test model',
                         params={'n_estimators': 10}, type='RFC',
                         file=test_file)

    with status("Inserting dummy prediction... "):
        pr = models.Prediction.create(project=p, model=m, file=test_file, dataset=d)


if __name__ == "__main__":
    insert_test_data()
