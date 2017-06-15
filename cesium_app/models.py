import datetime
import os
import sys
import inspect
import time
import pandas as pd

import peewee as pw
from playhouse.postgres_ext import ArrayField, BinaryJSONField
from playhouse.shortcuts import model_to_dict
from playhouse import signals

from baselayer.app.json_util import to_json
from baselayer.app.models import BaseModel, User, db
from baselayer.app.model_util import filter_pw_models

from cesium import featurize


class Project(BaseModel):
    """ORM model of the Project table"""
    name = pw.CharField()
    description = pw.CharField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def all(username):
        user = User.get(username=username)
        return (Project
                .select()
                .join(UserProject)
                .where(UserProject.user == user)
                .order_by(Project.created))

    @staticmethod
    def add_by(name, description, username):
        user = User.get(username=username)
        with db.atomic():
            p = Project.create(name=name, description=description)
            UserProject.create(user=user, project=p)
        return p

    def is_owned_by(self, username):
        user = User.get(username=username)
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

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)

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
    custom_features_script = pw.CharField(null=True)  # move to fset file?
    file = pw.ForeignKeyField(File, on_delete='CASCADE')
    task_id = pw.CharField(null=True)
    finished = pw.DateTimeField(null=True)

    def is_owned_by(self, username):
        return self.project.is_owned_by(username)

    @staticmethod
    def get_if_owned(fset_id, username):
        try:
            f = Featureset.get(Featureset.id == fset_id)
        except Featureset.DoesNotExist:
            raise AccessError('No such feature set')

        if not f.is_owned_by(username):
            raise AccessError('No such feature set')

        return f


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

    def format_pred_data(fset, data):
        fset.columns = fset.columns.droplevel('channel')
        fset.index = fset.index.astype(str)  # can't use ints as JSON keys

        labels = pd.Series(data['labels'] if len(data.get('labels', [])) > 0
                           else None, index=fset.index)

        if len(data.get('pred_probs', [])) > 0:
            preds = pd.DataFrame(data.get('pred_probs', []),
                                 index=fset.index).to_dict(orient='index')
        else:
            preds = pd.Series(data['preds'], index=fset.index).to_dict()
        result = {name: {'features': feats, 'label': labels.loc[name],
                         'prediction': preds[name]}
                  for name, feats in fset.to_dict(orient='index').items()}
        return result

    def display_info(self):
        info = self.__dict__()
        info['model_type'] = self.model.type
        info['dataset_name'] = self.dataset.name
        info['model_name'] = self.model.name
        info['featureset_name'] = self.model.featureset.name
        if self.task_id is None:
            fset, data = featurize.load_featureset(self.file.uri)
            info['isProbabilistic'] = (len(data['pred_probs']) > 0)
            info['results'] = Prediction.format_pred_data(fset, data)
        return info


app_models = filter_pw_models(inspect.getmembers(sys.modules[__name__]))
