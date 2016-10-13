'''Assortment of fixtures for use in test modules.'''

import uuid
import os
from os.path import join as pjoin
from contextlib import contextmanager
from cesium_app import models as m
from cesium import build_model
from cesium import predict
from cesium import data_management
from cesium.features import CADENCE_FEATS, GENERAL_FEATS, LOMB_SCARGLE_FEATS
from cesium.tests import fixtures
from cesium_app.config import cfg
import shutil
import peewee
import datetime
from sklearn.externals import joblib
import xarray as xr


@contextmanager
def create_test_project():
    """Create and yield test project, then delete."""
    p = m.Project.add_by('test_proj', 'test_desc', 'testuser@gmail.com')
    p.save()
    try:
        yield p
    finally:
        p.delete_instance()


@contextmanager
def create_test_dataset(project, label_type='class'):
    """Create and yield test labeled dataset, then delete.

    Params
    ------
    project : `models.Project` instance
        The project under which to create test dataset.
    label_type  : str
        String indicating whether data labels are class names ('class')
        for classification, or numerical values for regression (anything other
        than 'class'). Defaults to 'class'.

    """
    if label_type == 'class':
        header = pjoin(os.path.dirname(__file__),
                       'data', 'asas_training_subset_classes.dat')
    elif label_type == 'regr':
        header = pjoin(os.path.dirname(__file__),
                       'data', 'asas_training_subset_targets.dat')
    tarball = pjoin(os.path.dirname(__file__),
                    'data', 'asas_training_subset.tar.gz')
    header = shutil.copy2(header, cfg['paths']['upload_folder'])
    tarball = shutil.copy2(tarball, cfg['paths']['upload_folder'])
    time_series = data_management.parse_and_store_ts_data(
        tarball, cfg['paths']['ts_data_folder'], header)
    ts_paths = [ts.path for ts in time_series]
    d = m.Dataset.add(name='test_ds', project=project, file_uris=ts_paths)
    d.save()
    try:
        yield d
    finally:
        d.delete_instance()


@contextmanager
def create_test_featureset(project, label_type='class'):
    """Create and yield test labeled featureset, then delete.

    Parameters
    ----------
    project : `models.Project` instance
        The project under which to create test feature set.
    label_type  : {'class', 'regr', 'none'}, optional
        String indicating whether data are labeled with class names ('class')
        for classification, numerical values for regression ('regr'), or
        unlabeled ('none'). Defaults to 'class'.

    """
    if label_type == 'class':
        targets = ['Mira', 'Classical_Cepheid']
    elif label_type == 'regr':
        targets = [2.2, 3.4, 4.4, 2.2, 3.1]
    elif label_type == 'none':
        targets = []
    features_to_use = (CADENCE_FEATS + GENERAL_FEATS + LOMB_SCARGLE_FEATS)
    fset_data = fixtures.sample_featureset(5, 1, features_to_use, targets)
    fset_path = pjoin(cfg['paths']['features_folder'],
                      '{}.nc'.format(str(uuid.uuid4())))
    fset_data.to_netcdf(fset_path, engine=cfg['xr_engine'])
    f, created = m.File.create_or_get(uri=fset_path)
    fset = m.Featureset.create(name='test_featureset', file=f, project=project,
                               features_list=features_to_use,
                               custom_features_script=None,
                               finished=datetime.datetime.now())
    fset.save()
    try:
        yield fset
    finally:
        fset.delete_instance()


@contextmanager
def create_test_model(fset, model_type='RandomForestClassifier'):
    """Create and yield test model, then delete.

    Params
    ------
    fset : `models.Featureset` instance
        The (labeled) feature set from which to build the model.
    model_type  : str, optional
        String indicating type of model to build. Defaults to
        'RandomForestClassifier'.

    """
    model_params = {
        "RandomForestClassifier": {
            "bootstrap": True, "criterion": "gini",
            "oob_score": False, "max_features": "auto",
            "n_estimators": 10},
        "RandomForestRegressor": {
            "bootstrap": True, "criterion": "mse",
            "oob_score": False, "max_features": "auto",
            "n_estimators": 10},
        "LinearSGDClassifier": {
            "loss": "hinge"},
        "LinearRegressor": {
            "fit_intercept": True}}
    with xr.open_dataset(fset.file.uri, engine=cfg['xr_engine']) as fset_data:
        model_data = build_model.build_model_from_featureset(fset_data,
                                                             model_type=model_type)
        model_path = pjoin(cfg['paths']['models_folder'],
                           '{}.pkl'.format(str(uuid.uuid4())))
        joblib.dump(model_data, model_path)
    f, created = m.File.create_or_get(uri=model_path)
    model = m.Model.create(name='test_model',
                           file=f, featureset=fset, project=fset.project,
                           params=model_params[model_type], type=model_type,
                           finished=datetime.datetime.now())
    model.save()
    try:
        yield model
    finally:
        model.delete_instance()


@contextmanager
def create_test_prediction(dataset, model):
    """Create and yield test prediction, then delete.

    Params
    ------
    dataset : `models.Dataset` instance
        The dataset on which prediction will be performed.
    model  : `models.Model` instance
        The model to use to create prediction.

    """
    with xr.open_dataset(model.featureset.file.uri, engine=cfg['xr_engine']) as fset_data:
        model_data = joblib.load(model.file.uri)
        pred_data = predict.model_predictions(fset_data.load(), model_data)
    pred_path = pjoin(cfg['paths']['predictions_folder'],
                      '{}.nc'.format(str(uuid.uuid4())))
    pred_data.to_netcdf(pred_path, engine=cfg['xr_engine'])
    f, created = m.File.create_or_get(uri=pred_path)
    pred = m.Prediction.create(file=f, dataset=dataset, project=dataset.project,
                               model=model, finished=datetime.datetime.now())
    pred.save()
    try:
        yield pred
    finally:
        pred.delete_instance()
