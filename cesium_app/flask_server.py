#!/usr/bin/python

import os
from os.path import join as pjoin
import tarfile
import time

from flask import (
    Flask, request, session, Response, send_from_directory)
import uuid
from werkzeug.utils import secure_filename
import jwt
import datetime
import traceback
import requests

from .config import cfg
from cesium import obs_feature_tools as oft
from cesium import science_feature_tools as sft
from cesium import data_management
from cesium import custom_exceptions

from .json_util import to_json

from . import models as m
from .flow import Flow
from . import util
from .ext.sklearn_models import (
    model_descriptions as sklearn_model_descriptions
    )
from . import plot

# Flask initialization
app = Flask(__name__, static_url_path='', static_folder='../public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

flow = Flow()

# TODO: FIXME!
def get_username():
    return "testuser@gmail.com"  # get_current_userkey()


@app.before_request
def before_request():
    N = 5
    for i in range(1, N + 1):
        try:
            m.db.connect()
        except Exception as e:
            if (i == N):
                raise e
            else:
              print('Error connecting to database -- sleeping for a while')
              time.sleep(5)


@app.after_request
def after_request(response):
    m.db.close()
    return response


class UnauthorizedAccess(Exception):
    pass


def error(message):
    return to_json(
        {
            "status": "error",
            "message": message
        })


# TODO only push messages to relevant user (what about task_complete?)
def success(data={}, action=None, payload=None):
    if action is not None:
        flow.push(get_username(), action, payload or {})

    return to_json(
        {
            "status": "success",
            "data": data
        })


from functools import wraps
def exception_as_error(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(traceback.format_exc())
            return error(str(e))

    return wrapper


# TODO pass in user somehow
# TODO show error notification for failures
@app.route("/task_complete", methods=['POST'])
def task_complete():
    data = request.get_json()
    if 'fset_id' in data:
        fset = m.Featureset.get(m.Featureset.id == data['fset_id'])
        if data['status'] == 'success':
            fset.task_id = None
            fset.finished = datetime.datetime.now()
            fset.save()
            success(action='cesium/SHOW_NOTIFICATION',
                    payload={"note": "Featureset '{}' finished.".format(fset.name)})
            return success({"id": fset.id}, 'cesium/FETCH_FEATURESETS')
        elif data['status'] == 'error':
            fset.delete_instance()
            success(action='cesium/SHOW_NOTIFICATION',
                    payload={"note": "Featureset '{}' failed. Please try"
                             " again".format(fset.name), "type": "error"})
            return success({"id": fset.id}, 'cesium/FETCH_FEATURESETS')
    elif 'model_id' in data:
        model = m.Model.get(m.Model.id == data['model_id'])
        if data['status'] == 'success':
            model.task_id = None
            model.finished = datetime.datetime.now()
            model.save()
            success(action='cesium/SHOW_NOTIFICATION',
                    payload={"note": "Model '{}' finished.".format(model.name)})
            return success({"id": model.id}, 'cesium/FETCH_MODELS')
        elif data['status'] == 'error':
            model.delete_instance()
            success(action='cesium/SHOW_NOTIFICATION',
                    payload={"note": "Model '{}' failed."
                             " Please try again.".format(model.name),
                             "type": "error"})
            return success({"id": model.id}, 'cesium/FETCH_MODELS')
    elif 'prediction_id' in data:
        prediction = m.Prediction.get(m.Prediction.id == data['prediction_id'])
        if data['status'] == 'success':
            prediction.task_id = None
            prediction.finished = datetime.datetime.now()
            prediction.save()
            success(action='cesium/SHOW_NOTIFICATION',
                    payload={"note": "Prediction '{}'/'{}'"
                             " finished.".format(prediction.dataset.name,
                                                prediction.model.name)})
            return success({"id": prediction.id}, 'cesium/FETCH_PREDICTIONS')
        elif data['status'] == 'error':
            prediction.delete_instance()
            success(action='cesium/SHOW_NOTIFICATION',
                    payload={"note": "Prediction '{}'/'{}' failed. Please try"
                             " again.".format(prediction.dataset.name,
                                            prediction.model.name),
                             "type": "error" })
            return success({"id": prediction.id}, 'cesium/FETCH_PREDICTIONS')
    else:
        raise ValueError('Unrecognized task type')


@app.route("/project", methods=["GET", "POST"])
@app.route("/project/<project_id>", methods=["GET", "PUT", "DELETE"])
@exception_as_error
def Project(project_id=None):
    """
    """
    # First, make sure the user owns the project they are trying to
    # manipulate
    result = {}

    if project_id is not None:
        p = m.Project.get(m.Project.id == project_id)

        if not p.is_owned_by(get_username()):
            raise RuntimeError("User not authorized")

    if request.method == 'POST':
        data = request.get_json()

        p = m.Project.add_by(data['projectName'],
                             data.get('projectDescription', ''),
                             get_username())

        return success({"id": p.id}, 'cesium/FETCH_PROJECTS')

    elif request.method == "GET":
        if project_id is not None:
            proj_info = m.Project.get(m.Project.id == project_id)
        else:
            proj_info = m.Project.all(get_username())

        return success(proj_info)

    elif request.method == "PUT":
        if project_id is None:
            raise RuntimeError("No project ID provided")

        data = request.get_json()
        query = m.Project.update(
            name=data['projectName'],
            description=data.get('projectDescription', ''),
            ).where(m.Project.id == project_id)
        query.execute()

        return success(action='cesium/FETCH_PROJECTS')

    elif request.method == "DELETE":
        if project_id is None:
            raise RuntimeError("No project ID provided")

        p = m.Project.get(m.Project.id == project_id)
        p.delete_instance()

        return success(action='cesium/FETCH_PROJECTS')


@app.route('/dataset', methods=['POST', 'GET'])
@app.route('/dataset/<dataset_id>', methods=['GET', 'PUT', 'DELETE'])
@exception_as_error
def Dataset(dataset_id=None):
    """
    """
    if dataset_id:
        d = m.Dataset.get(m.Dataset.id == dataset_id)
        if not d.project.is_owned_by(get_username()):
            raise error('Unauthorized access')

    if request.method == 'POST':
        form = request.form

        if not 'tarFile' in request.files:
            return error('No tar file uploaded')

        zipfile = request.files['tarFile']

        if zipfile.filename == '':
            return error('Empty tar file uploaded')

        dataset_name = form['datasetName']
        project_id = form['projectID']

        zipfile_name = (str(uuid.uuid4()) + "_" +
                        str(secure_filename(zipfile.filename)))
        zipfile_path = pjoin(cfg['paths']['upload_folder'], zipfile_name)
        zipfile.save(zipfile_path)

        # Header file is optional for unlabled data w/o metafeatures
        if 'headerFile' in request.files:
            headerfile = request.files['headerFile']
            headerfile_name = (str(uuid.uuid4()) + "_" +
                               str(secure_filename(headerfile.filename)))
            headerfile_path = pjoin(cfg['paths']['upload_folder'], headerfile_name)
            headerfile.save(headerfile_path)
        else:
            headerfile_path = None

        p = m.Project.get(m.Project.id == project_id)
        # TODO this should give unique names to the time series files
        time_series = data_management.parse_and_store_ts_data(
            zipfile_path,
            cfg['paths']['ts_data_folder'],
            headerfile_path)
        ts_paths = [ts.path for ts in time_series]
        d = m.Dataset.add(name=dataset_name, project=p, file_uris=ts_paths)

        return success(d, 'cesium/FETCH_DATASETS')

    elif request.method == "GET":
        if dataset_id is None:
            datasets = [d for p in m.Project.all(get_username())
                            for d in p.datasets]
        else:
            datasets = d

        return success(datasets)

    elif request.method == "DELETE":
        if dataset_id is None:
            raise error('No dataset specified')

        d.delete_instance()

        return success(action='cesium/FETCH_DATASETS')


@app.route('/features', methods=['POST', 'GET'])
@app.route('/features/<featureset_id>', methods=['GET', 'PUT', 'DELETE'])
@exception_as_error
def Features(featureset_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        data = request.get_json()
        featureset_name = data.get('featuresetName', '')
        dataset_id = int(data['datasetID'])
        feature_fields = {feature: selected for (feature, selected) in
                          data.items() if feature.startswith(('sci_', 'obs_',
                                                              'lmb_'))}
        feat_type_name = [feat.split('_', 1) for (feat, selected) in
                          feature_fields.items() if selected]
        features_to_use = [fname for (ftype, fname) in feat_type_name]

        custom_feats_code = data['customFeatsCode'].strip()

        if not features_to_use:
            return error("At least one feature must be selected.")

        # Not working yet:
        if custom_feats_code and 0:
            custom_features_script = pjoin(
                cfg['paths']['upload_folder'], "custom_feature_scripts",
                str(uuid.uuid4()) + ".py")
            with open(custom_features_script, 'w') as f:
                f.write(custom_feats_code)
            # TODO: Extract list of custom features from code
            custom_features = [] # request.form.getlist("Custom Features List")
            features_to_use += custom_features
        else:
            custom_features_script = None

        fset_path = pjoin(cfg['paths']['features_folder'],
                          '{}_featureset.nc'.format(uuid.uuid4()))

        dataset = m.Dataset.get(m.Dataset.id == dataset_id)

        fset = m.Featureset.create(name=featureset_name,
                                   file=m.File.create(uri=fset_path),
                                   project=dataset.project,
                                   features_list=features_to_use,
                                   custom_features_script=custom_features_script)
        res = featurize_and_notify(get_username(), fset.id, dataset.uris,
                                   features_to_use, fset_path,
                                   custom_features_script)
        fset.task_id = res
        fset.save()

        return success(fset, 'cesium/FETCH_FEATURESETS')

    elif request.method == 'GET':
        if featureset_id is not None:
            featureset_info = m.Featureset.get(m.Featureset.id == featureset_id)
        else:
            featureset_info = [f for p in m.Project.all(get_username())
                               for f in p.featuresets]
        return success(featureset_info)

    elif request.method == 'DELETE':
        if featureset_id is None:
            return error("Invalid request - feature set ID not provided.")

        f = m.Featureset.get(m.Featureset.id == featureset_id)
        if f.is_owned_by(get_username()):
            f.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return success(action='cesium/FETCH_FEATURESETS')
    elif request.method == 'PUT':
        if featureset_id is None:
            return error("Invalid request - feature set ID not provided.")

        # TODO!
        return error("Functionality for this endpoint is not yet implemented.")


@app.route('/models', methods=['POST', 'GET'])
@app.route('/models/<model_id>', methods=['GET', 'PUT', 'DELETE'])
@exception_as_error
def Models(model_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        data = request.get_json()

        model_name = data.pop('modelName')
        featureset_id = data.pop('featureSet')
        # TODO remove cast once this is passed properly from the front end
        model_type = sklearn_model_descriptions[int(data.pop('modelType'))]['name']
        project_id = data.pop('project')

        fset = m.Featureset.get(m.Featureset.id == featureset_id)
        if fset.finished is None:
            raise RuntimeError("Can't build model for in-progress featureset.")

        model_params = data

        model_params = {k: util.robust_literal_eval(v)
                        for k, v in model_params.items()}

        # TODO split out constant params / params to optimize
        model_params, params_to_optimize = model_params, {}
        util.check_model_param_types(model_type, model_params)

        model_path = pjoin(cfg['paths']['models_folder'],
                           '{}_model.nc'.format(uuid.uuid4()))

        model_file = m.File.create(uri=model_path)
        model = m.Model.create(name=model_name, file=model_file,
                               featureset=fset, project=fset.project,
                               params=model_params, type=model_type)

        res = build_model_and_notify(get_username(), model.id, model_type,
                                     model_params, fset.file.uri,
                                     model_file.uri,
                                     params_to_optimize)
        model.task_id = res
        model.save()

        return success(data={'message': "We're working on your model"},
                       action='cesium/FETCH_MODELS')

    elif request.method == 'GET':
        if model_id is not None:
            model_info = m.Model.get(m.Model.id == model_id)
        else:
            model_info = [model for p in m.Project.all(get_username())
                          for model in p.models]
        return success(model_info)

    elif request.method == 'DELETE':
        if model_id is None:
            return error("Invalid request - model set ID not provided.")

        f = m.Model.get(m.Model.id == model_id)
        if f.is_owned_by(get_username()):
            f.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return success(action='cesium/FETCH_MODELS')

    elif request.method == 'PUT':
        if model_id is None:
            return error("Invalid request - model set ID not provided.")

        return error("Functionality for this endpoint is not yet implemented.")


@app.route('/predictions', methods=['POST', 'GET'])
@app.route('/predictions/<prediction_id>', methods=['GET', 'PUT', 'DELETE'])
@exception_as_error
def predictions(prediction_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        data = request.get_json()

        dataset_id = data['datasetID']
        model_id = data['modelID']

        dataset = m.Dataset.get(m.Dataset.id == data["datasetID"])
        model = m.Model.get(m.Model.id == data["modelID"])
        if model.finished is None:
            raise RuntimeError("Can't predict for in-progress model.")
        fset = model.featureset
        if fset.finished is None:
            raise RuntimeError("Can't predict for in-progress featureset.")
        prediction_path = pjoin(cfg['paths']['predictions_folder'],
                                '{}_prediction.nc'.format(uuid.uuid4()))
        prediction_file = m.File.create(uri=prediction_path)
        prediction = m.Prediction.create(file=prediction_file, dataset=dataset,
                                         project=dataset.project, model=model)
        res = predict_and_notify(get_username(), prediction.id, dataset.uris,
            fset.features_list, model.file.uri, prediction_path,
            custom_features_script=fset.custom_features_script)

        prediction.task_id = res
        prediction.save()

        return success(prediction, 'cesium/FETCH_PREDICTIONS')

    elif request.method == 'GET':
        if prediction_id is not None:
            prediction = m.Prediction.get(m.Prediction.id == prediction_id)
            prediction_info = prediction.display_info()
        else:
            predictions = [prediction for p in m.Project.all(get_username())
                           for prediction in p.predictions]
            prediction_info = [p.display_info() for p in predictions]
        return success(prediction_info)

    elif request.method == 'DELETE':
        if prediction_id is None:
            return error("Invalid request - prediction set ID not provided.")

        f = m.Prediction.get(m.Prediction.id == prediction_id)
        if f.is_owned_by(get_username()):
            f.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return success(action='cesium/FETCH_PREDICTIONS')

    elif request.method == 'PUT':
        if prediction_id is None:
            return error("Invalid request - prediction set ID not provided.")

        return error("Functionality for this endpoint is not yet implemented.")


@app.route("/features_list", methods=["GET"])
@exception_as_error
def get_features_list():
    if request.method == "GET":
        return success({
            "obs_features": oft.FEATURES_LIST,
            "sci_features": [el for el in sft.FEATURES_LIST if el not in
                             sft.LOMB_SCARGLE_FEATURES_LIST],
            "lmb_features": sft.LOMB_SCARGLE_FEATURES_LIST})


# !!!
# This API call should **only be callable by logged in users**
# !!!
@app.route('/socket_auth_token', methods=['GET'])
@exception_as_error
def socket_auth_token():
    secret = cfg['flask']['secret-key']
    token = jwt.encode({
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'username': get_username()
        }, secret)
    return success({'token': token})


@app.route("/sklearn_models", methods=["GET"])
@exception_as_error
def sklearn_models():
    return success(sklearn_model_descriptions)


@app.route('/plot_features/<featureset_id>', methods=['GET'])
@exception_as_error
def PlotFeatures(featureset_id):
    fset = m.Featureset.get(m.Featureset.id == featureset_id)
    if not fset.is_owned_by(get_username()):
        raise RuntimeError("User not authorized")
    features_to_plot = sorted(fset.features_list)[0:4]
    data, layout = plot.feature_scatterplot(fset.file.uri, features_to_plot)
    return success({'data': data, 'layout': layout})


# TODO where do these belong? new module? here? inline above?
# TODO where do task server params live?
def featurize_and_notify(username, fset_id, ts_paths, features_to_use,
                         fset_path, custom_features_script=None):
    payload = {'type': 'featurize',
               'params': {'ts_paths': ts_paths,
                          'features_to_use': features_to_use,
                          'output_path': fset_path},
               'metadata': {'fset_id': fset_id, 'username': username}}
    result = requests.post('http://127.0.0.1:63000/task',
                           json=payload).json()
    if result['status'] == 'success':
        return result['data']['task_id']
    else:
        raise RuntimeError("Featurization failed: {}".format(result['message']))


def build_model_and_notify(username, model_id, model_type, model_params,
                           fset_path, model_path, params_to_optimize={}):
    payload = {'type': 'build_model',
               'params': {'model_type': model_type,
                          'model_params': model_params,
                          'fset_path': fset_path,
                          'output_path': model_path,
                          'params_to_optimize': params_to_optimize},
               'metadata': {'model_id': model_id, 'username': username}}
    result = requests.post('http://127.0.0.1:63000/task',
                           json=payload).json()
    if result['status'] == 'success':
        return result['data']['task_id']
    else:
        raise RuntimeError("Model building failed: {}".format(result['message']))


def predict_and_notify(username, prediction_id, ts_paths, features_to_use,
                       model_path, prediction_path,
                       custom_features_script=None):
    payload = {'type': 'predict',
               'params': {'ts_paths': ts_paths,
                          'features_to_use': features_to_use,
                          'model_path': model_path,
                          'output_path': prediction_path},
               'metadata': {'prediction_id': prediction_id, 'username': username}}
    result = requests.post('http://127.0.0.1:63000/task',
                           json=payload).json()
    if result['status'] == 'success':
        return result['data']['task_id']
    else:
        raise RuntimeError("Prediction failed: {}".format(result['message']))
