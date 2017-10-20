import textwrap

from baselayer.app.env import load_env
from baselayer.app.model_util import status, create_tables, drop_tables
from cesium_app import models


def insert_test_data():
    with status("Dropping all tables"):
        drop_tables()

    with status("Creating tables"):
        create_tables()

    for model in models.Base.metadata.tables:
        print('    -', model)

    USERNAME = 'testuser@cesium-ml.org'
    with status(f"Creating dummy user: {USERNAME}... "):
        u = models.User(username=USERNAME)
        models.DBSession().add(u)
        models.DBSession().commit()

    for i in range(3):
        with status("Inserting dummy project"):
            p = models.Project(name=f'test project {i}', users=[u])
            models.DBSession().add(p)
            models.DBSession().commit()

        print(f"\n{textwrap.indent(str(p), '  ')}\n")

    with status("Assert that user has 3 projects"):
        assert len(u.projects) == 3

    with status("Inserting dummy dataset and time series... "):
        files = [models.DatasetFile(uri=f'/dir/ts{i}.npz') for i in range(3)]
        d = models.Dataset(name='test dataset', project=p, files=files)
        models.DBSession().add_all(files + [d])
        models.DBSession().commit()

    with status("Inserting dummy featureset... "):
        f = models.Featureset(project=p, name='test featureset',
                              file_uri='/dir/fset.npz',
                              features_list=['amplitude'])
        models.DBSession().add(f)
        models.DBSession().commit()

    with status("Inserting dummy model... "):
        m = models.Model(project=p, featureset=f, name='test model',
                         params={'n_estimators': 10}, type='RFC',
                         file_uri='/tmp/blah.pkl')
        models.DBSession().add(m)
        models.DBSession().commit()

    with status("Inserting dummy prediction... "):
        pr = models.Prediction(project=p, model=m, file_uri='/tmp/blergh.pkl', dataset=d)
        models.DBSession().add(pr)
        models.DBSession().commit()


def create_token_user(bot_name, project_ids):
    u = models.User(username=bot_name)
    p = models.Project.query.filter(models.Project.id.in_(project_ids)).all()
    u.projects.extend(p)
    t = models.Token(user=u)
    models.DBSession().add_all([u, t])
    models.DBSession().commit()
    return t.id


if __name__ == "__main__":
    env, cfg = load_env()

    with status(f"Connecting to database {cfg['database']['database']}"):
        models.init_db(**cfg['database'])

    insert_test_data()
