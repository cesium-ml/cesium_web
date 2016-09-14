from .base import BaseHandler, AccessError
from ..models import Prediction, File, Dataset, Model, Project
from ..config import cfg

import tornado.gen

import cesium.time_series
import cesium.featurize
import cesium.predict

import xarray as xr
from sklearn.externals import joblib
from os.path import join as pjoin
import uuid
import datetime


class PredictionHandler(BaseHandler):
    def _get_prediction(self, prediction_id):
        try:
            d = Prediction.get(Prediction.id == prediction_id)
        except Prediction.DoesNotExist:
            raise AccessError('No such dataset')

        if not d.is_owned_by(self.get_username()):
            raise AccessError('No such dataset')

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

        dataset = Dataset.get(Dataset.id == data["datasetID"])
        model = Model.get(Model.id == data["modelID"])

        username = self.get_username()

        if not (dataset.is_owned_by(username) and model.is_owned_by(username)):
            return self.error('No access to dataset or model')

        fset = model.featureset
        if (model.finished is None) or (fset.finished is None):
            return self.error('Computation of model or feature set still in progress')

        prediction_path = pjoin(cfg['paths']['predictions_folder'],
                                '{}_prediction.nc'.format(uuid.uuid4()))
        prediction_file = File.create(uri=prediction_path)
        prediction = Prediction.create(file=prediction_file, dataset=dataset,
                                       project=dataset.project, model=model)

        executor = yield self._get_executor()

        all_time_series = executor.map(cesium.time_series.from_netcdf,
                                       dataset.uris)
        all_features = executor.map(cesium.featurize.featurize_single_ts,
                                    all_time_series,
                                    features_to_use=fset.features_list,
                                    custom_script_path=fset.custom_features_script)
        fset_data = executor.submit(cesium.featurize.assemble_featureset,
                                    all_features, all_time_series)
        model_data = executor.submit(joblib.load, model.file.uri)
        predset = executor.submit(cesium.predict.model_predictions,
                                  fset_data, model_data)
        future = executor.submit(xr.Dataset.to_netcdf, predset,
                                 prediction_path, engine=cfg['xr_engine'])

        prediction.task_id = future.key
        prediction.save()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_prediction, future, prediction)

        return self.success(prediction, 'cesium/FETCH_PREDICTIONS')

    def get(self, prediction_id=None):
        if prediction_id is None:
            predictions = [prediction
                           for project in Project.all(self.get_username())
                           for prediction in project.predictions]
            prediction_info = [p.display_info() for p in predictions]
        else:
            prediction = self._get_prediction(prediction_id)

        return self.success(prediction_info)

    def delete(self, prediction_id):
        prediction = self._get_prediction(prediction_id)
        prediction.delete_instance()
        return self.success(action='cesium/FETCH_PREDICTIONS')
