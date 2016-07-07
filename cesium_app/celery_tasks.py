from celery.signals import task_success
import requests

from cesium import featurize, build_model, predict
from cesium.celery_tasks import (
    featurize_task, build_model_task, prediction_task)
from .celery_app import app
from .config import cfg


@app.task()
def report_finished(data):
    """Callback that notifies web app when a task is finished.

    Call with report_finished.si(data=data) (immutable signature) to avoid
    passing in result of previous tasks.
    """
    r = requests.post('{}/task_complete'.format(cfg['server']['url']),
                      json=data)
    #return r.json()['status']


def featurize_and_notify(username, fset_id, ts_paths, features_to_use,
                         output_path, custom_script_path=None):
    """Returns Celery task that computes features and notifies the web app
    when the computation is complete.
    """
    data = {'status': 'success', 'fset_id': fset_id, 'username': username}
    return (featurize_task(ts_paths, features_to_use, output_path,
                           custom_script_path) | report_finished.si(data=data))


def build_model_and_notify(username, model_id, model_type, model_params,
                           fset_path, output_path, params_to_optimize=None):
    """Returns Celery task that trains model and notifies the web app when the
    computation is complete.
    """
    data = {'status': 'success', 'model_id': model_id, 'username': username}
    return (build_model_task.s(model_type, model_params, fset_path,
                               output_path, params_to_optimize) |
            report_finished.si(data=data))


def predict_and_notify(username, ts_paths, features_to_use, model, output_path,
                       custom_features_script=None):
    """Returns Celery task that makes predictions and notifies the web app when
    the computation is complete.
    """
    data = {'status': 'success', 'prediction_id': prediction_id, 'username': username}
    return (prediction_task(ts_paths, features_to_use, model, output_path,
                            custom_features_script) |
            report_finished.si(data=data))
