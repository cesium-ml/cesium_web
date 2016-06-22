import datetime
import inspect
import sys

import peewee as pw
from playhouse.fields import ManyToManyField
from playhouse.postgres_ext import ArrayField, BinaryJSONField
from playhouse.shortcuts import model_to_dict
from json_util import to_json

from config import cfg


db = pw.PostgresqlDatabase(**cfg['database'], autocommit=True,
                           autorollback=True)


class UnauthorizedAccess(Exception):
    pass


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

    @staticmethod
    def delete_by(project_id, by_user):
        p = Project.get(Project.id == project_id)
        users = [o.username for o in p.owners]
        if by_user in users:
            p.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")


class UserProject(BaseModel):
    username = pw.CharField()
    project = pw.ForeignKeyField(Project, related_name='owners',
                                 on_delete='CASCADE')

    class Meta:
        indexes = (
            (('username', 'project'), True),
        )


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
    files = ManyToManyField(File)

    @staticmethod
    def add(name, project, file_uris=[]):
        with db.atomic():
            d = Dataset.create(name=name, project=project)
            d.files, created = zip(*(
                File.create_or_get(uri=uri) for uri in file_uris)
                )
        return d


DatasetFileThrough = Dataset.files.get_through_model()


class Featureset(BaseModel):
    """ORM model of the Featureset table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='featuresets')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)

    # could potentially live in the file
    custom_features_script = pw.CharField(null=True)

    file = pw.ForeignKeyField(File, on_delete='CASCADE')


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


class Prediction(BaseModel):
    """ORM model of the Prediction table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='predictions')
    model = pw.ForeignKeyField(Model, on_delete='CASCADE',
                               related_name='predictions')
    created = pw.DateTimeField(default=datetime.datetime.now)
    file = pw.ForeignKeyField(File, on_delete='CASCADE')


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
    file_uris = ['/dir/ts{}.nc'.format(i) for i in range(3)]
    d = Dataset.add(name='test dataset', project=p, file_uris=file_uris)

    print("Inserting dummy featureset...")
    test_file = File.get()
    f = Featureset.create(project=p, dataset=d, name='test featureset',
                          file=test_file)

    print("Inserting dummy model...")
    m = Model.create(project=p, featureset=f, name='test model',
                     params={'n_estimators': 10}, type='RFC',
                     file=test_file)

    print("Inserting dummy prediction...")
    pr = Prediction.create(project=p, model=m, file=test_file)
