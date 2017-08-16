'''Assortment of fixtures for use in test modules.'''

import uuid
import os
from os.path import join as pjoin
from cesium_app.models import (DBSession, User, Project, DatasetFile, Dataset,
                               Featureset, Model, Prediction)
from cesium import data_management, featurize, time_series
from cesium.tests.fixtures import sample_featureset
from cesium.features import CADENCE_FEATS, GENERAL_FEATS, LOMB_SCARGLE_FEATS
from cesium_app.ext.sklearn_models import MODELS_TYPE_DICT
import shutil
import datetime
import joblib
import pandas as pd
from tempfile import mkdtemp

import factory


TMP_DIR = mkdtemp()


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = DBSession()
        sqlalchemy_session_persistence = 'commit'
        model = Project
    name = 'test_proj'
    description = 'test_desc'
    users = []

    @factory.post_generation
    def set_user(project, create, extracted, **kwargs):
        if not create:
            return
        project.users = User.query.filter(User.username ==
                                          'testuser@cesium-ml.org').all()
        DBSession().commit()


class DatasetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = DBSession()
        sqlalchemy_session_persistence = 'commit'
        model = Dataset
    name = 'class'
    project = factory.SubFactory(ProjectFactory)

    @factory.post_generation
    def add_files(dataset, create, value, *args, **kwargs):
        if not create:
            return

        if 'class' in dataset.name:
            header = pjoin(os.path.dirname(__file__),
                           'data', 'asas_training_subset_classes.dat')
        elif 'regr' in dataset.name:
            header = pjoin(os.path.dirname(__file__),
                           'data', 'asas_training_subset_targets.dat')
        else:
            header = None
        tarball = pjoin(os.path.dirname(__file__),
                        'data', 'asas_training_subset.tar.gz')
        header = shutil.copy2(header, TMP_DIR) if header else None
        tarball = shutil.copy2(tarball, TMP_DIR)
        ts_paths = data_management.parse_and_store_ts_data(
            tarball, TMP_DIR, header)

        dataset.files = [DatasetFile(uri=uri) for uri in ts_paths]
        DBSession().commit()


class FeaturesetFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = DBSession()
        sqlalchemy_session_persistence = 'commit'
        model = Featureset
    project = factory.SubFactory(ProjectFactory)
    name = 'class',
    features_list = (CADENCE_FEATS + GENERAL_FEATS + LOMB_SCARGLE_FEATS)
    finished = datetime.datetime.now()

    @factory.post_generation
    def add_file(featureset, create, value, *args, **kwargs):
        if not create:
            return

        if 'class' in featureset.name:
            labels = ['Mira', 'Classical_Cepheid']
        elif 'regr' in featureset.name:
            labels = [2.2, 3.4, 4.4, 2.2, 3.1]
        else:
            labels = []
        fset_data, fset_labels = sample_featureset(5, 1,
                                                   featureset.features_list,
                                                   labels)
        fset_path = pjoin(TMP_DIR, '{}.npz'.format(str(uuid.uuid4())))
        featurize.save_featureset(fset_data, fset_path, labels=fset_labels)
        featureset.file_uri = fset_path
        DBSession().commit()


class ModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = DBSession()
        sqlalchemy_session_persistence = 'commit'
        model = Model
    project = factory.SubFactory(ProjectFactory)
    name = 'test_model'
    featureset = factory.SubFactory(FeaturesetFactory)
    type = 'RandomForestClassifier'
    params = {}
    finished = datetime.datetime.now()

    @factory.post_generation
    def add_file(model, create, value, *args, **kwargs):
        model_params = {
            "RandomForestClassifier": {
                "bootstrap": True, "criterion": "gini",
                "oob_score": False, "max_features": "auto",
                "n_estimators": 10, "random_state": 0},
            "RandomForestRegressor": {
                "bootstrap": True, "criterion": "mse",
                "oob_score": False, "max_features": "auto",
                "n_estimators": 10},
            "LinearSGDClassifier": {
                "loss": "hinge"},
            "LinearRegressor": {
                "fit_intercept": True}}
        fset_data, data = featurize.load_featureset(model.featureset.file_uri)
        model_data = MODELS_TYPE_DICT[model.type](**model_params[model.type])
        model_data.fit(fset_data, data['labels'])
        model.file_uri = pjoin('/tmp/', '{}.pkl'.format(str(uuid.uuid4())))
        joblib.dump(model_data, model.file_uri)
        DBSession().commit()


class PredictionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = DBSession()
        sqlalchemy_session_persistence = 'commit'
        model = Prediction
    project = factory.SubFactory(ProjectFactory)
    dataset = factory.SubFactory(DatasetFactory)
    model = factory.SubFactory(ModelFactory)
    finished = datetime.datetime.now()

    @factory.post_generation
    def add_file(prediction, create, value, *args, **kwargs):
        train_featureset = prediction.model.featureset
        fset_data, data = featurize.load_featureset(train_featureset.file_uri)
        if 'class' in prediction.dataset.name or 'regr' in prediction.dataset.name:
            labels = data['labels']
        else:
            labels = []
        model_data = joblib.load(prediction.model.file_uri)
        if hasattr(model_data, 'best_estimator_'):
            model_data = model_data.best_estimator_
        preds = model_data.predict(fset_data)
        pred_probs = (pd.DataFrame(model_data.predict_proba(fset_data),
                                   index=fset_data.index.astype(str),
                                   columns=model_data.classes_)
                      if hasattr(model_data, 'predict_proba') else [])
        all_classes = model_data.classes_ if hasattr(model_data, 'classes_') else []
        pred_path = pjoin(TMP_DIR, '{}.npz'.format(str(uuid.uuid4())))
        featurize.save_featureset(fset_data, pred_path, labels=labels,
                                  preds=preds, pred_probs=pred_probs)
        prediction.file_uri = pred_path
        DBSession().commit()
