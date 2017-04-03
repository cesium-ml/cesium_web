from .base import BaseHandler, AccessError
from ..models import Prediction, File, Dataset, Model, Project
from ..config import cfg
from .. import util

import tornado.gen
from tornado.web import RequestHandler
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
    def _get_prediction(self, prediction_id):
        try:
            d = Prediction.get(Prediction.id == prediction_id)
        except Prediction.DoesNotExist:
            raise AccessError('No such prediction')

        if not d.is_owned_by(self.get_username()):
            raise AccessError('No such prediction')

        return d

    @tornado.gen.coroutine
    def _await_prediction(self, future, prediction):
        try:
            result = yield future._result()

            prediction.task_id = None
            prediction.finished = datetime.datetime.now()
            prediction.save()

            self.action('cesium/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction '{}/{}' completed.".format(
                                prediction.dataset.name,
                                prediction.model.name)
                            })

        except Exception as e:
            prediction.delete_instance()
            self.action('cesium/SHOW_NOTIFICATION',
                        payload={
                            "note": "Prediction '{}/{}'" " failed "
                            "with error {}. Please try again.".format(
                                prediction.dataset.name,
                                prediction.model.name, e),
                             "type": "error"
                            })

        self.action('cesium/FETCH_PREDICTIONS')

    @tornado.gen.coroutine
    def post(self):
        data = self.get_json()

        dataset_id = data['datasetID']
        model_id = data['modelID']
        # If only a subset of specified dataset is to be used, a list of the
        # corresponding time series file names can be provided
        ts_names = data.get('ts_names')

        dataset = Dataset.get(Dataset.id == data["datasetID"])
        model = Model.get(Model.id == data["modelID"])

        username = self.get_username()

        if not (dataset.is_owned_by(username) and model.is_owned_by(username)):
            return self.error('No access to dataset or model')

        fset = model.featureset
        if (model.finished is None) or (fset.finished is None):
            return self.error('Computation of model or feature set still in progress')

        pred_path = pjoin(cfg['paths']['predictions_folder'],
                          '{}_prediction.npz'.format(uuid.uuid4()))
        prediction_file = File.create(uri=pred_path)
        prediction = Prediction.create(file=prediction_file, dataset=dataset,
                                       project=dataset.project, model=model)

        executor = yield self._get_executor()

        # If only a subset of the dataset is to be used, get specified files
        if ts_names:
            ts_uris = [f.uri for f in dataset.files if os.path.basename(f.name)
                       in ts_names or os.path.basename(f.name).split('.npz')[0]
                       in ts_names]
        else:
            ts_uris = dataset.uris

        all_time_series = executor.map(time_series.load, ts_uris)
        all_labels = executor.map(lambda ts: ts.label, all_time_series)
        all_features = executor.map(featurize.featurize_single_ts,
                                    all_time_series,
                                    features_to_use=fset.features_list,
                                    custom_script_path=fset.custom_features_script)
        fset_data = executor.submit(featurize.assemble_featureset,
                                    all_features, all_time_series)
        imputed_fset = executor.submit(featurize.impute_featureset,
                                       fset_data, inplace=False)
        model_or_gridcv = executor.submit(joblib.load, model.file.uri)
        model_data = executor.submit(lambda model: model.best_estimator_
                                     if hasattr(model, 'best_estimator_') else model,
                                     model_or_gridcv)
        preds = executor.submit(lambda fset, model: model.predict(fset),
                                imputed_fset, model_data)
        pred_probs = executor.submit(lambda fset, model: model.predict_proba(fset)
                                     if hasattr(model, 'predict_proba') else [],
                                     imputed_fset, model_data)
        all_classes = executor.submit(lambda model: model.classes_
                                      if hasattr(model, 'classes_') else [],
                                      model_data)
        future = executor.submit(featurize.save_featureset, imputed_fset,
                                 pred_path, labels=all_labels, preds=preds,
                                 pred_probs=pred_probs, all_classes=all_classes)

        prediction.task_id = future.key
        prediction.save()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_prediction, future, prediction)

        return self.success(prediction.display_info(), 'cesium/FETCH_PREDICTIONS')

    def get(self, prediction_id=None, action=None):
        if action == 'download':
            pred_path = self._get_prediction(prediction_id).file.uri
            fset, data = featurize.load_featureset(pred_path)
            result = pd.DataFrame({'ts_name': fset.index,
                                   'label': data['labels'],
                                   'prediction': data['preds']},
                                  columns=['ts_name', 'label', 'prediction'])
            if data.get('pred_probs'):
                result['probability'] = np.max(data['pred_probs'], axis=1)
            self.set_header("Content-Type", 'text/csv; charset="utf-8"')
            self.set_header("Content-Disposition", "attachment; "
                            "filename=cesium_prediction_results.csv")
            self.write(result.to_csv(index=False))
        else:
            if prediction_id is None:
                predictions = [prediction
                               for project in Project.all(self.get_username())
                               for prediction in project.predictions]
                prediction_info = [p.display_info() for p in predictions]
            else:
                prediction = self._get_prediction(prediction_id)
                prediction_info = prediction.display_info()

            return self.success(prediction_info)

    def delete(self, prediction_id):
        prediction = self._get_prediction(prediction_id)
        prediction.delete_instance()
        return self.success(action='cesium/FETCH_PREDICTIONS')


class PredictRawDataHandler(BaseHandler):
    def post(self):
        ts_data = json_decode(self.get_argument('ts_data'))
        model_id = json_decode(self.get_argument('modelID'))
        meta_feats = json_decode(self.get_argument('meta_features', 'null'))
        impute_kwargs = json_decode(self.get_argument('impute_kwargs', '{}'))

        model = Model.get(Model.id == model_id)
        model_data = joblib.load(model.file.uri)
        if hasattr(model_data, 'best_estimator_'):
            model_data = model_data.best_estimator_
        features_to_use = model.featureset.features_list

        fset = featurize.featurize_time_series(*ts_data,
                                               features_to_use=features_to_use,
                                               meta_features=meta_feats)
        fset = featurize.impute_featureset(fset, **impute_kwargs)
        data = {'preds': model_data.predict(fset),
                'all_classes': model_data.classes_}
        if hasattr(model_data, 'predict_proba'):
            data['pred_probs'] = model_data.predict_proba(fset)
        pred_info = Prediction.format_pred_data(fset, data)
        return self.success(pred_info)
