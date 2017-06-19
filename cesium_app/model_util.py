import textwrap

from baselayer.app.model_util import status, create_tables, drop_tables
from cesium_app import models


def insert_test_data():
    with status("Dropping all tables"):
        drop_tables()

    with status("Creating tables"):
        create_tables()

    for model in models.Base.metadata.tables:
        print('    -', model)

    USERNAME = 'testuser@gmail.com'
    with status(f"Creating dummy user: {USERNAME}... "):
        u = models.User(username=USERNAME, email=USERNAME)
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
                         file=test_file)
        models.DBSession().add(m)
        models.DBSession().commit()

    with status("Inserting dummy prediction... "):
        pr = models.Prediction(project=p, model=m, file=test_file, dataset=d)
        models.DBSession().add(pr)
        models.DBSession().commit()


if __name__ == "__main__":
    insert_test_data()
