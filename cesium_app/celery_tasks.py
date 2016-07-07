from celery.signals import task_success
import requests

from cesium import featurize, build_model, predict
from cesium.celery_tasks import (
    featurize_task, build_model_task, prediction_task)
from .celery_app import app


@app.task()
def report_finished(*args, **kwargs):
    r = requests.post('http://localhost:5000/task_complete',
                      json=kwargs['data'])
    #return r.json()['status']


def featurize_and_notify(fset_id, ts_paths, features_to_use, output_path,
                         custom_script_path=None):
    data = {'status': 'success', 'fset_id': fset_id}
    return (featurize_task(ts_paths, features_to_use, output_path,
                           custom_script_path) | report_finished.si(data=data))


def build_model_and_notify(model_id, model_type, model_params, fset_path,
                           output_path, params_to_optimize=None):
    data = {'status': 'success', 'model_id': model_id}
    return (build_model_task.s(model_type, model_params, fset_path,
                               output_path, params_to_optimize) |
            report_finished.si(data=data))


def predict_and_notify(ts_paths, features_to_use, model, output_path,
                       custom_features_script=None):
    data = {'status': 'success', 'prediction_id': prediction_id}
    return (prediction_task(ts_paths, features_to_use, model, output_path,
                            custom_features_script) |
            report_finished.si(data=data))
