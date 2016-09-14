from .base import BaseHandler, AccessError
from ..models import Project, Model, Featureset, File
from ..ext.sklearn_models import (
    model_descriptions as sklearn_model_descriptions,
    check_model_param_types
    )
from ..util import robust_literal_eval
from ..config import cfg

from os.path import join as pjoin
import uuid
import datetime

from cesium import build_model
import tornado.ioloop
from sklearn.externals import joblib
import xarray as xr


class ModelHandler(BaseHandler):
    def _get_model(self, model_id):
        try:
            m = Model.get(Model.id == model_id)
        except Model.DoesNotExist:
            raise AccessError('No such model')

        if not m.is_owned_by(self.get_username()):
            raise AccessError('No such project')

        return m

    def get(self, model_id=None):
        if model_id is not None:
            model_info = self._get_model(model_id)
        else:
            model_info = [model for p in Project.all(self.get_username())
                          for model in p.models]

        return self.success(model_info)

    @tornado.gen.coroutine
    def _await_model(self, future, model):
        try:
            result = yield future._result()

            model.task_id = None
            model.finished = datetime.datetime.now()
            model.save()

            self.action('cesium/SHOW_NOTIFICATION',
                        payload={"note": "Model '{}' computed.".format(model.name)})

        except Exception as e:
            model.delete_instance()
            self.action('cesium/SHOW_NOTIFICATION',
                        payload={"note": "Cannot create model '{}': {}".format(model.name, e),
                                 "type": 'error'})

        self.action('cesium/FETCH_MODELS')

    @tornado.gen.coroutine
    def post(self):
        data = self.get_json()

        model_name = data.pop('modelName')
        featureset_id = data.pop('featureSet')
        # TODO remove cast once this is passed properly from the front end
        model_type = sklearn_model_descriptions[int(data.pop('modelType'))]['name']
        project_id = data.pop('project')

        fset = Featureset.get(Featureset.id == featureset_id)
        if not fset.is_owned_by(self.get_username()):
            return self.error('No access to featureset')

        if fset.finished is None:
            return self.error('Cannot build model for in-progress featureset')

        model_params = data
        model_params = {k: robust_literal_eval(v)
                        for k, v in model_params.items()}

        # TODO split out constant params / params to optimize
        model_params, params_to_optimize = model_params, {}
        check_model_param_types(model_type, model_params)

        model_path = pjoin(cfg['paths']['models_folder'],
                           '{}_model.pkl'.format(uuid.uuid4()))

        model_file = File.create(uri=model_path)
        model = Model.create(name=model_name, file=model_file,
                             featureset=fset, project=fset.project,
                             params=model_params, type=model_type)

        executor = yield self._get_executor()

        fset_data = executor.submit(lambda path: xr.open_dataset(path, engine=cfg['xr_engine']),
                                    fset.file.uri)
        computed_model = executor.submit(
            build_model.build_model_from_featureset,
            featureset=fset_data, model_type=model_type,
            model_options=model_params,
            params_to_optimize=params_to_optimize)
        future = executor.submit(joblib.dump, computed_model, model_file.uri)
        closed = executor.submit(xr.Dataset.close, fset_data)

        model.task_id = future.key
        model.save()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_model, future, model)

        return self.success(data={'message': "Model training begun."},
                            action='cesium/FETCH_MODELS')


    def delete(self, model_id):
        m = self._get_model(model_id)
        m.delete_instance()

        return self.success(action='cesium/FETCH_MODELS')
