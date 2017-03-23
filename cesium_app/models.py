import datetime
import inspect
import os
import sys
import time

import peewee as pw
from playhouse.postgres_ext import ArrayField, BinaryJSONField
from playhouse.shortcuts import model_to_dict
from playhouse import signals
import xarray as xr

from cesium_app.json_util import to_json
from cesium_app.config import cfg

from social_peewee.storage import (
    database_proxy,
    BasePeeweeStorage, PeeweeAssociationMixin, PeeweeCodeMixin,
    PeeweeNonceMixin, PeeweePartialMixin, PeeweeUserMixin)


db = pw.PostgresqlDatabase(autocommit=True, autorollback=True,
                           **cfg['database'])
database_proxy.initialize(db)


class BaseModel(signals.Model):
    def __str__(self):
        return to_json(self.__dict__())

    def __dict__(self):
        return model_to_dict(self, recurse=False, backrefs=False)

    class Meta:
        database = db


class User(BaseModel):
    username = pw.CharField(unique=True)
    email = pw.CharField(unique=True)

    @classmethod
    def user_model(cls):
        return User

    def is_authenticated(self):
        return True

    def is_active(self):
        return True


class UserSocialAuth(BaseModel, PeeweeUserMixin):
    user = pw.ForeignKeyField(User, related_name='social_auth')

    @classmethod
    def user_model(cls):
        return User


class TornadoStorage(BasePeeweeStorage):
    class nonce(PeeweeNonceMixin):
        """Single use numbers"""
        pass

    class association(PeeweeAssociationMixin):
        """OpenId account association"""
        pass

    class code(PeeweeCodeMixin):
        """Mail validation single one time use code"""
        pass

    class partial(PeeweePartialMixin):
        pass

    user = UserSocialAuth


class Project(BaseModel):
    """ORM model of the Project table"""
    name = pw.CharField()
    description = pw.CharField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def all(user):
        return (Project
                .select()
                .join(UserProject)
                .where(UserProject.user == user)
                .order_by(Project.created))

    @staticmethod
    def add_by(name, description, user):
        with db.atomic():
            p = Project.create(name=name, description=description)
            UserProject.create(user=user, project=p)
        return p

    def is_owned_by(self, user):
        users = [owner.user for owner in self.owners]
        return user in users


class UserProject(BaseModel):
    user = pw.ForeignKeyField(User, related_name='projects')
    project = pw.ForeignKeyField(Project, related_name='owners',
                                 on_delete='CASCADE')

    class Meta:
        indexes = (
            (('user', 'project'), True),
        )


class File(BaseModel):
    """ORM model of the TimeSeries table"""
    uri = pw.CharField(primary_key=True)  # s3://cesium_bin/3eef6601a
    name = pw.CharField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.now)

@signals.post_delete(sender=File)
def remove_file_after_delete(sender, instance):
    try:
        os.remove(instance.uri)
    except FileNotFoundError:
        pass


class Dataset(BaseModel):
    """ORM model of the Dataset table"""
    project = pw.ForeignKeyField(Project, on_delete='CASCADE',
                                 related_name='datasets')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)
    meta_features = ArrayField(pw.CharField)

    @staticmethod
    def add(name, project, file_uris=[], file_names=[], meta_features=[]):
        if not file_names:
            file_names = file_uris
        with db.atomic():
            d = Dataset.create(name=name, project=project,
                               meta_features=meta_features)
            for fname, uri in zip(file_names, file_uris):
                f, created = File.get_or_create(name=fname, uri=uri)
                DatasetFile.create(dataset=d, file=f)
        return d

    @property
    def uris(self):
        return [f.uri for f in self.files]

    @property
    def file_names(self):
        return [f.name for f in self.files]

    @property
    def files(self):
        query = File.select().join(DatasetFile).join(Dataset).where(Dataset.id
                                                                    == self.id)
        return list(query.execute())

    def is_owned_by(self, user):
        return self.project.is_owned_by(user)

    def display_info(self):
        info = self.__dict__()
        info['files'] = [os.path.basename(fname)
                         for fname in self.file_names]

        return info


class DatasetFile(BaseModel):
    dataset = pw.ForeignKeyField(Dataset, on_delete='CASCADE')
    file = pw.ForeignKeyField(File, on_delete='CASCADE')

    class Meta:
        indexes = (
            (('dataset', 'file'), True),
        )

@signals.pre_delete(sender=Dataset)
def remove_related_files(sender, instance):
    for f in instance.files:
        f.delete_instance()


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

    def is_owned_by(self, user):
        return self.project.is_owned_by(user)


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
    train_score = pw.FloatField(null=True)

    def is_owned_by(self, user):
        return self.project.is_owned_by(user)


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

    def is_owned_by(self, user):
        return self.project.is_owned_by(user)

    def display_info(self):
        info = self.__dict__()
        info['model_type'] = self.model.type
        info['dataset_name'] = self.dataset.name
        info['model_name'] = self.model.name
        info['featureset_name'] = self.model.featureset.name
        if self.task_id is None:
            try:
                with xr.open_dataset(self.file.uri) as pset:
                    info['results'] = pset.load()
            except (RuntimeError, OSError):
                info['results'] = None
        if 'results' in info and info['results']:
            first_result = info['results'].sel(name=info['results'].name.values[0])
            if 'prediction' in first_result:
                info['isProbabilistic'] = 'class_label' in\
                                          first_result.prediction
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
        # This will probably break; add a real user to the DB first
        u = UserProject.create(user=USERNAME, project=p)
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
