from baselayer.app.handlers.base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from baselayer.app.access import auth_or_token
from ..models import DBSession, Project, Model, Featureset
from ..ext.sklearn_models import (
    model_descriptions as sklearn_model_descriptions,
    check_model_param_types, MODELS_TYPE_DICT
    )
from ..util import robust_literal_eval
from cesium import featurize

from os.path import join as pjoin
import uuid
import datetime

import sklearn
from sklearn.model_selection import GridSearchCV
import joblib

import tornado.ioloop


def _build_model_compute_statistics(fset_path, model_type, model_params,
                                    params_to_optimize, model_path):
    '''Build model and return summary statistics.

    Parameters
    ----------
    fset_path : str
        Path to feature set .npz file.
    model_type : str
        Type of model to be built, e.g. 'RandomForestClassifier'.
    model_params : dict
        Dictionary with hyperparameter values to be used in model building.
        Keys are parameter names, values are the associated parameter values.
        These hyperparameters will be passed to the model constructor as-is
        (for hyperparameter optimization, see `params_to_optimize`).
    params_to_optimize : dict or list of dict
        During hyperparameter optimization, various model parameters
        are adjusted to give an optimal fit. This dictionary gives the
        different values that should be explored for each parameter. E.g.,
        `{'alpha': [1, 2], 'beta': [4, 5, 6]}` would fit models on all
        6 combinations of alpha and beta and compare the resulting models'
        goodness-of-fit. If None, only those hyperparameters specified in
        `model_parameters` will be used (passed to model constructor as-is).
    model_path : str
        Path indicating where serialized model will be saved.

    Returns
    -------
    score : float
        The model's training score.
    best_params : dict
        Dictionary of best hyperparameter values (keys are parameter names,
        values are the corresponding best values) determined by `scikit-learn`'s
        `GridSearchCV`. If no hyperparameter optimization is performed (i.e.
        `params_to_optimize` is None or is an empty dict, this will be an empty
        dict.
    '''
    fset, data = featurize.load_featureset(fset_path)
    if len(data['labels']) != len(fset):
        raise ValueError("Cannot build model for unlabeled feature set.")
    n_jobs = (model_params.pop('n_jobs') if 'n_jobs' in model_params
              and params_to_optimize else -1)
    model = MODELS_TYPE_DICT[model_type](**model_params)
    if params_to_optimize:
        model = GridSearchCV(model, params_to_optimize,
                             n_jobs=n_jobs)
    model.fit(fset, data['labels'])

    metrics = {}
    metrics['train_score'] = model.score(fset, data['labels'])

    best_params = model.best_params_ if params_to_optimize else {}
    joblib.dump(model, model_path)

    if model_type == 'RandomForestClassifier':
        if params_to_optimize:
            model = model.best_estimator_
        if hasattr(model, 'oob_score_'):
            metrics['oob_score'] = model.oob_score_
        if hasattr(model, 'feature_importances_'):
            metrics['feature_importances'] = dict(zip(
                fset.columns.get_level_values(0).tolist(),
                model.feature_importances_.tolist()))

    return metrics, best_params


class ModelHandler(BaseHandler):
    @auth_or_token
    def get(self, model_id=None, action=None):
        if action == 'download':
            model = Model.get_if_owned_by(model_id, self.current_user)
            model_path = model.file_uri
            with open(model_path, 'rb') as f:
                model_data = f.read()
            self.set_header("Content-Type", "application/octet-stream")
            self.set_header(
                "Content-Disposition", "attachment; "
                f"filename=cesium_model_{model.project.name}"
                f"_{model.name}_{str(model.finished).replace(' ', 'T')}"
                f"_joblib_v{joblib.__version__}"
                f"_sklearn_v{sklearn.__version__}.pkl")
            self.write(model_data)
        else:
            if model_id is not None:
                model_info = Model.get_if_owned_by(model_id, self.current_user)
            else:
                model_info = [model for p in self.current_user.projects
                              for model in p.models]

            return self.success(model_info)

    @auth_or_token
    async def _await_model_statistics(self, model_stats_future, model):
        try:
            model_metrics, best_params = await model_stats_future

            model = DBSession().merge(model)
            model.task_id = None
            model.finished = datetime.datetime.now()
            model.metrics = model_metrics
            model.params.update(best_params)
            DBSession().commit()

            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={"note": "Model '{}' computed.".format(model.name)})

        except Exception as e:
            DBSession().delete(model)
            DBSession().commit()
            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={"note": "Cannot create model '{}': {}".format(model.name, e),
                                 "type": 'error'})
            print('Error creating model:', type(e), e)

        self.action('cesium/FETCH_MODELS')

    @auth_or_token
    async def post(self):
        data = self.get_json()

        model_name = data.pop('modelName')
        featureset_id = data.pop('featureset')

        model_type = sklearn_model_descriptions[int(data.pop('modelType'))]['name']
        project_id = data.pop('project')

        fset = Featureset.query.filter(Featureset.id == featureset_id).one()
        if not fset.is_owned_by(self.current_user):
            return self.error('No access to featureset')

        if fset.finished is None:
            return self.error('Cannot build model for in-progress feature set')

        model_params = data
        model_params = {k: robust_literal_eval(v)
                        for k, v in model_params.items()}

        model_params, params_to_optimize = check_model_param_types(model_type,
                                                                   model_params)
        model_type = model_type.split()[0]
        model_path = pjoin(self.cfg['paths:models_folder'],
                           '{}_model.pkl'.format(uuid.uuid4()))

        model = Model(name=model_name, file_uri=model_path,
                      featureset=fset, project=fset.project,
                      params=model_params, type=model_type)
        DBSession().add(model)

        client = await self._get_client()

        model_stats_future = client.submit(
            _build_model_compute_statistics, fset.file_uri, model_type,
            model_params, params_to_optimize, model_path)

        model.task_id = model_stats_future.key
        DBSession().commit()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_model_statistics, model_stats_future, model)

        return self.success(data={'message': "Model training begun."},
                            action='cesium/FETCH_MODELS')

    @auth_or_token
    def delete(self, model_id):
        m = Model.get_if_owned_by(model_id, self.current_user)
        DBSession().delete(m)
        DBSession().commit()

        return self.success(action='cesium/FETCH_MODELS')
