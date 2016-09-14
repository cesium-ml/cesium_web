import datetime
import inspect
import sys
import time

import peewee as pw
from playhouse.fields import ManyToManyField
from playhouse.postgres_ext import ArrayField, BinaryJSONField
from playhouse.shortcuts import model_to_dict
import xarray as xr

from cesium_app.json_util import to_json
from cesium_app.config import cfg


db = pw.PostgresqlDatabase(autocommit=True, autorollback=True,
                           **cfg['database'])


class BaseModel(pw.Model):
    def __str__(self):
        return to_json(self.__dict__())

    def __dict__(self):
        return model_to_dict(self, recurse=False, backrefs=False)

    class Meta:
        database = db


class Project(BaseModel):
    """ORM model of the Project table"""
    name = pw.CharField()
    description = pw.CharField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def all(username):
        return (Project
                .select()
                .join(UserProject)
                .where(UserProject.username == username)
                .order_by(Project.created))

    @staticmethod
    def add_by(name, description, username):
        with db.atomic():
            p = Project.create(name=name, description=description)
            UserProject.create(username=username, project=p)
        return p

    def is_owned_by(self, username):
        users = [o.username for o in self.owners]
        return username in users


class UserProject(BaseModel):
    username = pw.CharField()
    project = pw.ForeignKeyField(Project, related_name='owners',
                                 on_delete='CASCADE')

    class Meta:
        indexes = (
            (('username', 'project'), True),
        )


# TODO Delete corresponding file upon deleting row
class File(BaseModel):
    """ORM model of the TimeSeries table"""
    uri = pw.CharField(primary_key=True)  # s3://cesium_bin/3eef6601a
    created = pw.DateTimeField(default=datetime.datetime.now)


class Dataset(BaseModel):
    """ORM model of the Dataset table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='datasets')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def add(name, project, file_uris=[]):
        with db.atomic():
            d = Dataset.create(name=name, project=project)
            files, created = zip(*(
                File.create_or_get(uri=uri) for uri in file_uris)
            )
            for f in files:
                DatasetFile.create(dataset=d, file=f)
        return d

    @property
    def uris(self):
        query = File.select().join(DatasetFile).join(Dataset).where(Dataset.id
                                                                    == self.id)
        return [f.uri for f in query]

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)


class DatasetFile(BaseModel):
    dataset = pw.ForeignKeyField(Dataset, on_delete='CASCADE')
    file = pw.ForeignKeyField(File, on_delete='CASCADE')

    class Meta:
        indexes = (
            (('dataset', 'file'), True),
        )


class Featureset(BaseModel):
    """ORM model of the Featureset table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='featuresets')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)
    features_list = ArrayField(pw.CharField)
    custom_features_script = pw.CharField(null=True) # move to fset file?
    file = pw.ForeignKeyField(File, on_delete='CASCADE')
    task_id = pw.CharField(null=True)
    finished = pw.DateTimeField(null=True)

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)


class Model(BaseModel):
    """ORM model of the Model table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='models')
    featureset = pw.ForeignKeyField(Featureset, on_delete='CASCADE',
                                    related_name='models')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)
    params = BinaryJSONField(default={})
    type = pw.CharField()
    file = pw.ForeignKeyField(File, on_delete='CASCADE')
    task_id = pw.CharField(null=True)
    finished = pw.DateTimeField(null=True)

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)


class Prediction(BaseModel):
    """ORM model of the Prediction table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='predictions')
    dataset = pw.ForeignKeyField(Dataset, on_delete='CASCADE')
    model = pw.ForeignKeyField(Model, on_delete='CASCADE',
                               related_name='predictions')
    created = pw.DateTimeField(default=datetime.datetime.now)
    file = pw.ForeignKeyField(File, on_delete='CASCADE')
    task_id = pw.CharField(null=True)
    finished = pw.DateTimeField(null=True)

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)

    def display_info(self):
        info = self.__dict__()
        info['model_type'] = self.model.type
        info['dataset_name'] = self.dataset.name
        info['model_name'] = self.model.name
        info['featureset_name'] = self.model.featureset.name
        if self.task_id is None:
            try:
                with xr.open_dataset(self.file.uri, engine=cfg['xr_engine']) as pset:
                    info['results'] = pset.load()
            except (RuntimeError, OSError):
                info['results'] = None
        return info


models = [
    obj for (name, obj) in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(obj) and issubclass(obj, pw.Model)
    and not obj == BaseModel
]


def create_tables(retry=5):
    for i in range(1, retry + 1):
        try:
            db.create_tables(models, safe=True)
            return
        except Exception as e:
            if (i == retry):
                raise e
            else:
                print('Could not connect to database...sleeping 5')
                time.sleep(5)

def drop_tables():
    db.drop_tables(models, safe=True, cascade=True)


if __name__ == "__main__":
    print("Dropping all tables...")
    drop_tables()
    print("Creating tables: {}".format([m.__name__ for m in models]))
    create_tables()

    USERNAME = 'testuser@gmail.com'
    print("Inserting dummy projects...")
    for i in range(5):
        p = Project.create(name='test project {}'.format(i))
        print(p)

    print("Creating dummy project owners...")
    for i in range(3):
        p = Project.get(Project.id == i + 1)
        u = UserProject.create(username=USERNAME, project=p)
        print(u)

    print('ASSERT User should have 3 projects')
    print(to_json(p.all('testuser@gmail.com')))
    assert(len(list(p.all('testuser@gmail.com'))) == 3)

    print("Inserting dummy dataset and time series...")
    file_uris = ['/dir/ts{}.nc'.format(i) for i in range(3)]
    d = Dataset.add(name='test dataset', project=p, file_uris=file_uris)

    print("Inserting dummy featureset...")
    test_file = File.get()
    f = Featureset.create(project=p, dataset=d, name='test featureset',
                          features_list=['amplitude'], file=test_file)

    print("Inserting dummy model...")
    m = Model.create(project=p, featureset=f, name='test model',
                     params={'n_estimators': 10}, type='RFC',
                     file=test_file)

    print("Inserting dummy prediction...")
    pr = Prediction.create(project=p, model=m, file=test_file, dataset=d)
