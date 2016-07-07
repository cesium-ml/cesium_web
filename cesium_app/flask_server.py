#!/usr/bin/python

import os
from os.path import join as pjoin
import tarfile
import multiprocessing

from flask import (
    Flask, request, session, Response, send_from_directory)
import uuid
from werkzeug.utils import secure_filename
import jwt
import datetime

from .config import cfg
from cesium import obs_feature_tools as oft
from cesium import science_feature_tools as sft
from cesium import data_management
from cesium import custom_exceptions

from .json_util import to_json

from . import models as m
from .flow import Flow
from .celery_tasks import featurize_task, build_model_task, predict_task
from . import util
from .ext.sklearn_models import (
    model_descriptions as sklearn_model_descriptions
    )

# Flask initialization
app = Flask(__name__, static_url_path='', static_folder='../public')
app.add_url_rule('/', 'root',
                 lambda: app.send_static_file('index.html'))

flow = Flow()

# TODO: FIXME!
def get_username():
    return "testuser@gmail.com"  # get_current_userkey()


@app.before_request
def before_request():
    m.db.connect()


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
            return error(str(e))

    return wrapper


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

        if not 'headerFile' in request.files:
            return error('No header file uploaded')

        if not 'tarFile' in request.files:
            return error('No tar file uploaded')

        headerfile = request.files['headerFile']
        zipfile = request.files['tarFile']

        if zipfile.filename == '':
            return error('Empty tar file uploaded')

        if headerfile.filename == '':
            return error('Empty header file uploaded')

        dataset_name = form['datasetName']
        project_id = form['projectID']

        # files have the following attributes:
        #
        # 'close', 'content_length', 'content_type', 'filename', 'headers',
        # 'mimetype', 'mimetype_params', 'name', 'save', 'stream']

        # Create unique file names
        headerfile_name = (str(uuid.uuid4()) + "_" +
                           str(secure_filename(headerfile.filename)))
        zipfile_name = (str(uuid.uuid4()) + "_" +
                        str(secure_filename(zipfile.filename)))
        headerfile_path = pjoin(cfg['paths']['upload_folder'], headerfile_name)
        zipfile_path = pjoin(cfg['paths']['upload_folder'], zipfile_name)
        headerfile.save(headerfile_path)
        zipfile.save(zipfile_path)

        p = m.Project.get(m.Project.id == project_id)
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

    elif request.method == "PUT":
        if dataset_id is None:
            raise error('No dataset specified')

        return error('Dataset updating not yet implemented')


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
        datasetID = int(data['datasetID'])
        feature_fields = {feature: selected for (feature, selected) in
                          data.items() if feature.startswith(('sci_', 'obs_'))}
        feat_type_name = [feat.split('_', 1) for (feat, selected) in
                          feature_fields.items() if selected]
        features_to_use = [fname for (ftype, fname) in feat_type_name]

        custom_feats_code = data['customFeatsCode'].strip()

        # Not working yet:
        if custom_feats_code and 0:
            custom_script_path = pjoin(
                cfg['paths']['upload_folder'], "custom_feature_scripts",
                str(uuid.uuid4()) + ".py")
            with open(custom_script_path, 'w') as f:
                f.write(custom_feats_code)
            # TODO: Extract list of custom features from code
            custom_features = [] # request.form.getlist("Custom Features List")
            features_to_use += custom_features
        else:
            custom_script_path = None

        fset_path = pjoin(cfg['paths']['features_folder'],
                          '{}_featureset.nc'.format(uuid.uuid4()))

        dataset = m.Dataset.get(m.Dataset.id == datasetID)

        fset = m.Featureset.create(name=featureset_name,
                                   file=m.File.create(uri=fset_path),
                                   project=dataset.project,
                                   custom_features_script=custom_script_path)
        res = featurize_task.delay(dataset.uris, fset_path, features_to_use,
                                   custom_script_path)

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

 # {'min_weight_fraction_leaf': 0, 'criterion': 'gini', 'min_samples_leaf': 1, 'max_depth': 'None', 'max_leaf_nodes': 'None', 'min_samples_split': 2, 'n_estimators': 10, 'random_state': 'None', 'max_features': 'auto', 'oob_score': False, 'modelType': 0, 'bootstrap': True, 'class_weight': 'None'}

        model_name = data.pop('modelName')
        model_id = data.pop('featureSet')
        model_type = sklearn_model_descriptions[data.pop('modelType')]['name']
        project_id = data.pop('project')

        fset = m.Featureset.get(m.Featureset.id == model_id)

        model_params = data

        model_params = {k: util.robust_literal_eval(v)
                        for k, v in model_params.items()}

        util.check_model_param_types(model_type, model_params)

        model_path = pjoin(cfg['paths']['models_folder'],
                           '{}_model.nc'.format(uuid.uuid4()))

        model_file = m.File.create(uri=model_path)
        model = m.Model(name=model_name, file=model_file, featureset=fset,
                        project=fset.project, params=model_params,
                        type=model_type)

        model = build_model_task.delay(model_path, model_type, model_params,
                                       fset.file.uri)

        return success(model)

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

        return success()

    elif request.method == 'PUT':
        if model_id is None:
            return error("Invalid request - model set ID not provided.")

        return error("Functionality for this endpoint is not yet implemented.")


@app.route('/predictions', methods=['POST', 'GET'])
@app.route('/predictions/<prediction_id>', methods=['GET', 'PUT', 'DELETE'])
@exception_as_error
def Predictions(prediction_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        data = request.get_json()
        dataset = m.Dataset.get(m.Dataset.id == int(data["datasetID"]))
        model = m.Model.get(m.Model.id == data["modelID"])
        fset = model.featureset
        prediction_path = pjoin(cfg['paths']['predictions_folder'],
                                '{}_prediction.nc'.format(uuid.uuid4()))
        prediction_file = m.Prediction.create(uri=prediction_path)
        prediction = m.Prediction(file=prediction_file, dataset=dataset,
                                  project=dataset.project, model=model)
        predict_task(dataset.uris, prediction_path, model.file.uri,
                     custom_features_script=fset.custom_features_script)
        return success()

    elif request.method == 'GET':
        if prediction_id is not None:
            prediction_info = m.Prediction.get(m.Prediction.id == prediction_id)
        else:
            prediction_info = [prediction for p in m.Project.all(get_username())
                          for prediction in p.predictions]
        return success(prediction_info)

    elif request.method == 'DELETE':
        if prediction_id is None:
            return error("Invalid request - prediction set ID not provided.")

        f = m.Prediction.get(m.Prediction.id == prediction_id)
        if f.is_owned_by(get_username()):
            f.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return to_json({"status": "success"})

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
            "sci_features": sft.FEATURES_LIST})


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
