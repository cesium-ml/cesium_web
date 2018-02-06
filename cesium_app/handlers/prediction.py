from baselayer.app.handlers.base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from baselayer.app.access import auth_or_token
from ..models import DBSession, Prediction, Dataset, Model, Project
from .. import util

import tornado.gen
from tornado.escape import json_decode

from cesium import featurize, time_series
from cesium.features import CADENCE_FEATS, GENERAL_FEATS, LOMB_SCARGLE_FEATS

import joblib
from os.path import join as pjoin
import uuid
import datetime
import os
import tempfile
import numpy as np
import pandas as pd


class PredictionHandler(BaseHandler):
    async def _await_prediction(self, future, prediction):
        try:
            result = await future

            prediction = DBSession().merge(prediction)
            prediction.task_id = None
            prediction.finished = datetime.datetime.now()
            DBSession().commit()

            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction '{}/{}' completed.".format(
                                prediction.dataset.name,
                                prediction.model.name)
                            })

        except Exception as e:
            DBSession().delete(prediction)
            DBSession().commit()
            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction '{}/{}'" " failed "
                            "with error {}. Please try again.".format(
                                prediction.dataset.name,
                                prediction.model.name, e),
                             "type": "error"
                            })

        self.action('cesium/FETCH_PREDICTIONS')

    @auth_or_token
    async def post(self):
        data = self.get_json()

        dataset_id = data['datasetID']
        model_id = data['modelID']
        # If only a subset of specified dataset is to be used, a list of the
        # corresponding time series file names can be provided
        ts_names = data.get('ts_names')

        dataset = Dataset.get_if_owned_by(data["datasetID"], self.current_user)
        model = Model.get_if_owned_by(data["modelID"], self.current_user)
        fset = model.featureset

        if (model.finished is None) or (fset.finished is None):
            return self.error('Computation of model or feature set still in progress')

        pred_path = os.path.abspath(pjoin(self.cfg['paths:predictions_folder'],
                                          '{}_prediction.npz'.format(uuid.uuid4())))
        prediction = Prediction(file_uri=pred_path, dataset=dataset,
                                project=dataset.project, model=model)
        DBSession().add(prediction)
        DBSession().commit()

        client = await self._get_client()

        # If only a subset of the dataset is to be used, get specified files
        ts_uris = [f.uri for f in dataset.files if not ts_names or
                   os.path.basename(f.name) in ts_names or
                   os.path.basename(f.name).split('.npz')[0] in ts_names]

        all_time_series = client.map(time_series.load, ts_uris)
        all_labels = client.map(lambda ts: ts.label, all_time_series)
        all_features = client.map(featurize.featurize_single_ts,
                                  all_time_series,
                                  features_to_use=fset.features_list,
                                  custom_script_path=fset.custom_features_script,
                                  raise_exceptions=False)
        fset_data = client.submit(featurize.assemble_featureset,
                                  all_features, all_time_series)
        imputed_fset = client.submit(featurize.impute_featureset,
                                     fset_data, inplace=False)
        model_or_gridcv = client.submit(joblib.load, model.file_uri)
        model_data = client.submit(lambda model: model.best_estimator_
                                   if hasattr(model, 'best_estimator_') else model,
                                   model_or_gridcv)
        preds = client.submit(lambda fset, model: model.predict(fset),
                              imputed_fset, model_data)
        pred_probs = client.submit(lambda fset, model:
                                   pd.DataFrame(model.predict_proba(fset),
                                                index=fset.index,
                                                columns=model.classes_)
                                   if hasattr(model, 'predict_proba') else [],
                                   imputed_fset, model_data)
        future = client.submit(featurize.save_featureset, imputed_fset,
                                 pred_path, labels=all_labels, preds=preds,
                                 pred_probs=pred_probs)

        prediction.task_id = future.key
        DBSession().add(prediction)
        DBSession().commit()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_prediction, future, prediction)

        return self.success(prediction.display_info(), 'cesium/FETCH_PREDICTIONS')

    @auth_or_token
    def get(self, prediction_id=None, action=None):
        if action == 'download':
            prediction = Prediction.get_if_owned_by(prediction_id, self.current_user)
            pred_path = prediction.file_uri
            fset, data = featurize.load_featureset(pred_path)
            result = pd.DataFrame(({'label': data['labels']}
                                   if len(data['labels']) > 0 else None),
                                  index=fset.index)
            if len(data.get('pred_probs', [])) > 0:
                result = pd.concat((result, data['pred_probs']), axis=1)
            else:
                result['prediction'] = data['preds']
            result.index.name = 'ts_name'
            self.set_header("Content-Type", 'text/csv; charset="utf-8"')
            self.set_header(
                "Content-Disposition", "attachment; "
                f"filename=cesium_prediction_results_{prediction.project.name}"
                f"_{prediction.dataset.name}"
                f"_{prediction.model.name}_{prediction.finished}.csv")
            self.write(result.to_csv(index=True))
        else:
            if prediction_id is None:
                predictions = [prediction
                               for project in self.current_user.projects
                               for prediction in project.predictions]
                prediction_info = [p.display_info() for p in predictions]
            else:
                prediction = Prediction.get_if_owned_by(prediction_id,
                                                        self.current_user)
                prediction_info = prediction.display_info()

            return self.success(prediction_info)

    @auth_or_token
    def delete(self, prediction_id):
        prediction = Prediction.get_if_owned_by(prediction_id,
                                                self.current_user)
        DBSession().delete(prediction)
        DBSession().commit()
        return self.success(action='cesium/FETCH_PREDICTIONS')


class PredictRawDataHandler(BaseHandler):
    @auth_or_token
    def post(self):
        ts_data = json_decode(self.get_argument('ts_data'))
        model_id = json_decode(self.get_argument('modelID'))
        meta_feats = json_decode(self.get_argument('meta_features', 'null'))
        impute_kwargs = json_decode(self.get_argument('impute_kwargs', '{}'))

        model = Model.query.get(model_id)
        model_data = joblib.load(model.file_uri)
        if hasattr(model_data, 'best_estimator_'):
            model_data = model_data.best_estimator_
        features_to_use = model.featureset.features_list

        fset = featurize.featurize_time_series(*ts_data,
                                               features_to_use=features_to_use,
                                               meta_features=meta_feats,
                                               raise_exceptions=False)
        fset = featurize.impute_featureset(fset, **impute_kwargs)
        fset.index = fset.index.astype(str)  # ensure JSON-encodable
        data = {'preds': model_data.predict(fset)}
        if hasattr(model_data, 'predict_proba'):
            data['pred_probs'] = pd.DataFrame(model_data.predict_proba(fset),
                                              index=fset.index,
                                              columns=model_data.classes_)
        else:
            data['pred_probs'] = []
        pred_info = Prediction.format_pred_data(fset, data)
        return self.success(pred_info)
