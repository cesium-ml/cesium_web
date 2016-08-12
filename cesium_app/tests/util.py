import uuid
import os
from os.path import join as pjoin
from contextlib import contextmanager
from cesium_app import models as m
from cesium import data_management
from cesium.obs_feature_tools import FEATURES_LIST as obs_feats_list
from cesium.science_feature_tools import FEATURES_LIST as sci_feats_list
from cesium_app.config import cfg
import shutil
import peewee
import datetime


@contextmanager
def test_project():
    p = m.Project.add_by('test_proj', 'test_desc', 'testuser@gmail.com')
    yield p
    p.delete_instance()


@contextmanager
def test_dataset(project=None):
    header = pjoin(os.path.dirname(__file__),
                   'data/asas_training_subset_classes.dat')
    tarball = pjoin(os.path.dirname(__file__),
                    'data/asas_training_subset.tar.gz')
    header = shutil.copy2(header, cfg['paths']['upload_folder'])
    tarball = shutil.copy2(tarball, cfg['paths']['upload_folder'])
    time_series = data_management.parse_and_store_ts_data(
        tarball, cfg['paths']['ts_data_folder'], header)
    ts_paths = [ts.path for ts in time_series]
    d = m.Dataset.add(name='test_ds', project=project, file_uris=ts_paths)
    yield d
    d.delete_instance()


@contextmanager
def test_featureset(project=None):
    features_to_use = obs_feats_list + sci_feats_list
    fset_path = pjoin(os.path.dirname(__file__),
                    'data/asas_training_subset_featureset.nc')
    fset_path = shutil.copy2(fset_path, cfg['paths']['ts_data_folder'])
    try:
        f = m.File.create(uri=fset_path)
    except peewee.IntegrityError:
        f = m.File.get(m.File.uri == fset_path)
    fset = m.Featureset.create(name='test_featureset',
                               file=f,
                               project=project,
                               features_list=features_to_use,
                               custom_features_script=None,
                               finished=datetime.datetime.now())
    yield fset
    fset.delete_instance()


@contextmanager
def test_model(fset=None):
    model_path = pjoin(os.path.dirname(__file__),
                    'data/test_rfc.nc')
    model_path = shutil.copy2(model_path, cfg['paths']['models_folder'])
    try:
        f = m.File.create(uri=model_path)
    except peewee.IntegrityError:
        f = m.File.get(m.File.uri == model_path)
    model = m.Model.create(name='test_model',
                           file=f,
                           featureset=fset,
                           project=fset.project,
                           params={},
                           type='RandomForestClassifier',
                           finished=datetime.datetime.now())
    yield model
    model.delete_instance()


@contextmanager
def test_prediction(ds=None, model=None):
    f_path = pjoin(os.path.dirname(__file__),
                    'data/asas_training_subset_featureset.nc')
    f_path = shutil.copy2(f_path, cfg['paths']['ts_data_folder'])

    try:
        f = m.File.create(uri=f_path)
    except peewee.IntegrityError:
        f = m.File.get(m.File.uri == f_path)

    pred = m.Prediction.create(file=f,
                               dataset=ds,
                               project=ds.project,
                               model=model,
                               finished=datetime.datetime.now())
    yield pred
    pred.delete_instance()
