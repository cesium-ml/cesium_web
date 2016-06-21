import datetime
import inspect
import sys

import peewee as pw
from playhouse.fields import ManyToManyField 
from playhouse.postgres_ext import ArrayField, HStoreField, BinaryJSONField
from playhouse.shortcuts import model_to_dict
from json_util import to_json

from config import cfg


db = pw.PostgresqlDatabase(**cfg['database'], autocommit=True,
                           autorollback=True)

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
    def add(name, description, username):
        with db.atomic():
            p = Project.create(name=name, description=description)
            UserProject.create(username=username, project=p)
        return p


class UserProject(BaseModel):
    username = pw.CharField()
    project = pw.ForeignKeyField(Project, related_name='owners',
                                 on_delete='CASCADE')

    class Meta:
        indexes = (
            (('username', 'project'), True),
        )


class TimeSeries(BaseModel):
    """ORM model of the TimeSeries table"""
    filename = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)


class Dataset(BaseModel):
    """ORM model of the Dataset table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='datasets')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)
    time_series = ManyToManyField(TimeSeries)

    @staticmethod
    def add(name, project, ts_paths=[]):
        with db.atomic():
            d = Dataset.create(name=name, project=project)
            # TODO createorget for ts_paths?
            d.time_series = [TimeSeries.create(filename=ts_path)
                             for ts_path in ts_paths]
        return d


TimeSeriesDataset = Dataset.time_series.get_through_model()


class Featureset(BaseModel):
    """ORM model of the Featureset table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='featuresets')
    dataset = pw.ForeignKeyField(Dataset, on_delete='CASCADE', null=True,
                                 related_name='featuresets')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)
    feat_list = ArrayField(pw.CharField, default=[])
    meta_feats = ArrayField(pw.CharField, default=[])
    pid = pw.IntegerField(null=True)
    custom_features_script = pw.CharField(null=True)
    filename = pw.CharField(null=True)
#    "headerfile_path": headerfile_path,
#    "zipfile_path": zipfile_path


class Model(BaseModel):
    """ORM model of the Model table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='models')
    featureset = pw.ForeignKeyField(Featureset, on_delete='CASCADE',
                                    related_name='models')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)
#    feat_list = ArrayField(pw.CharField)
#    meta_feats = ArrayField(pw.CharField, default=[]) # TODO why?
    pid = pw.IntegerField(null=True)
    params = BinaryJSONField(default={})
    type = pw.CharField()
    filename = pw.CharField(null=True)


class Prediction(BaseModel):
    """ORM model of the Prediction table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='predictions')
    model = pw.ForeignKeyField(Model, on_delete='CASCADE',
                               related_name='predictions')
    created = pw.DateTimeField(default=datetime.datetime.now)
    pid = pw.IntegerField(null=True)
    filename = pw.CharField(null=True)


models = [
    obj for (name, obj) in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(obj) and issubclass(obj, pw.Model)
    and not obj == BaseModel
]


def create_tables():
    db.create_tables(models, safe=True)


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
    ts_paths = ['/dir/ts{}.nc'.format(i) for i in range(3)]
    d = Dataset.add(name='test dataset', project=p, ts_paths=ts_paths)

    print("Inserting dummy featureset...")
    f = Featureset.create(project=p, dataset=d, name='test featureset',
                          feat_list=['f1', 'f2'], meta_fets=['meta1'])

    print("Inserting dummy model...")
    m = Model.create(project=p, featureset=f, name='test model',
                     params={'n_estimators': 10}, type='RFC')

    print("Inserting dummy prediction...")
    pr = Prediction.create(project=p, model=m)
