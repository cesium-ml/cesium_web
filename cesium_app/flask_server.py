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
from cesium import util as csutil

from .json_util import to_json

from . import models as m
from .flow import Flow
from .celery_tasks import featurize_task, build_model_task, predict_task

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


@app.route("/project", methods=["GET", "POST"])
@app.route("/project/<project_id>", methods=["GET", "PUT", "DELETE"])
def Project(project_id=None):
    """
    """
    if request.method == 'POST':
        data = request.get_json()
        try:
            m.Project.add_by(data['projectName'],
                             data.get('projectDescription', ''),
                             get_username())
        except Exception as e:
            return to_json(
                {
                    "status": "error",
                    "message": str(e)
                })

        flow.push(get_username(), 'cesium/FETCH_PROJECTS')

        return to_json({"status": "success"})

    elif request.method == "GET":
        if project_id is not None:
            proj_info = m.Project.get(m.Project.id == project_id)
        else:
            proj_info = m.Project.all(get_username())

        return to_json(
            {
                "status": "success",
                "data": proj_info
            })

    elif request.method == "PUT":
        if project_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - project ID not provided."
                })

        proj_name = str(request.form["Project Name"]).strip()
        proj_description = str(request.form["Description/notes"]).strip()

        query = m.Project.update(
            name=proj_name,
            description=proj_description,
            ).where(m.Project.id == project_id)
        query.execute()

        flow.push(get_username(), 'cesium/FETCH_PROJECTS')

    elif request.method == "DELETE":
        if project_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - project ID not provided."
                })
        p = m.Project.get(m.Project.id == project_id)
        if p.is_owned_by(get_username()):
            p.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        flow.push(get_username(), 'cesium/FETCH_PROJECTS')

        return to_json({"status": "success"})


@app.route('/get_state', methods=['GET'])
def get_state():
    """
    TODO change to use REST/CRUD
    """
    if request.method == 'GET':
        state = {}
        state["projectsList"] = m.Project.all(get_username())
        state["datasetsList"] = [d for p in state["projectsList"]
                                 for d in p.datasets]
        return Response(to_json(state),
                        mimetype='application/json',
                        headers={'Cache-Control': 'no-cache',
                                 'Access-Control-Allow-Origin': '*'})


@app.route('/dataset', methods=['POST', 'GET'])
@app.route('/dataset/<dataset_id>', methods=['GET', 'PUT', 'DELETE'])
def Dataset(dataset_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        dataset_name = str(request.form["Dataset Name"]).strip()
        headerfile = request.files["Header File"]
        zipfile = request.files["Tarball Containing Data"]

        if dataset_name == "":
            return to_json(
                {
                    "message": ("Dataset Title must contain non-whitespace "
                                "characters. Please try a different title."),
                    "type": "error"
                })

        project_id = request.form["Select Project"]

        # Create unique file names
        headerfile_name = (str(uuid.uuid4()) + "_" +
                           str(secure_filename(headerfile.filename)))
        zipfile_name = (str(uuid.uuid4()) + "_" +
                        str(secure_filename(zipfile.filename)))
        headerfile_path = pjoin(cfg['paths']['upload_folder'], headerfile_name)
        zipfile_path = pjoin(cfg['paths']['upload_folder'], zipfile_name)
        headerfile.save(headerfile_path)
        zipfile.save(zipfile_path)
        print("Saved", headerfile_name, "and", zipfile_name)

        p = m.Project.get(m.Project.id == project_id)
        time_series = data_management.parse_and_store_ts_data(
            zipfile_path,
            cfg['paths']['ts_data_folder'],
            headerfile_path)
        ts_paths = [ts.path for ts in time_series]
        d = m.Dataset.add(name=dataset_name, project=p, file_uris=ts_paths)

        return to_json({"status": "success"})
    elif request.method == "GET":
        if dataset_id is not None:
            dataset_info = m.Dataset.get(m.Dataset.id == dataset_id)
        else:
            dataset_info = [d for p in m.Project.all(get_username())
                            for d in p.datasets]

        return to_json(
            {
                "status": "success",
                "data": dataset_info
            })
    elif request.method == "DELETE":
        if dataset_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - data set ID not provided."
                })
        d = m.Dataset.get(m.Dataset.id == dataset_id)
        if d.is_owned_by(get_username()):
            d.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return to_json({"status": "success"})
    elif request.method == "PUT":
        if dataset_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - data set ID not provided."
                })
        # TODO!
        return to_json(
            {
                "status": "error",
                "message": "Functionality for this endpoint is not "
                           "yet implemented."
            })


@app.route('/features', methods=['POST', 'GET'])
@app.route('/features/<featureset_id>', methods=['GET', 'PUT', 'DELETE'])
def Features(featureset_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        featureset_name = request.form["Feature Set Title"].strip()
        dataset = m.Dataset.get(m.Dataset.id == request.form["Select Dataset"])
        features_to_use = request.form.getlist("Selected Features[]")
        custom_script_tested = (
            request.form["Custom Features Script Tested"].strip() == "true")
        if custom_script_tested:
            custom_script = request.files["Custom Features File"]
            custom_script_fname = str(secure_filename(custom_script.filename))
            custom_script_path = pjoin(
                    cfg['paths']['upload_folder'], "custom_feature_scripts",
                    str(uuid.uuid4()) + "_" + str(custom_script_fname))
            custom_script.save(custom_script_path)
            custom_features = request.form.getlist("Custom Features List")
            features_to_use += custom_features
        else:
            custom_script_path = None
        is_test = bool(request.form.get("is_test"))
        fset_path = pjoin(cfg['paths']['features_folder'],
                          '{}_featureset.nc'.format(uuid.uuid4()))
        fset = m.Featureset.create(name=featureset_name,
                                   file=m.File.create(uri=fset_path),
                                   project=dataset.project,
                                   custom_features_script=custom_script_path)
        res = featurize_task.delay(dataset.uris, fset_path, features_to_use,
                                   custom_script_path, is_test)
        return to_json({"status": "success"})
    elif request.method == 'GET':
        if featureset_id is not None:
            featureset_info = m.Featureset.get(m.Featureset.id == featureset_id)
        else:
            featureset_info = [f for p in m.Project.all(get_username())
                               for f in p.featuresets]
        return to_json(
            {
                "status": "success",
                "data": featureset_info
            })
    elif request.method == 'DELETE':
        if featureset_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - feature set ID not provided."
                })
        f = m.Featureset.get(m.Featureset.id == featureset_id)
        if f.is_owned_by(get_username()):
            f.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return to_json({"status": "success"})
    elif request.method == 'PUT':
        if featureset_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - feature set ID not provided."
                })
        # TODO!
        return to_json(
            {
                "status": "error",
                "message": "Functionality for this endpoint is not yet implemented."
            })


@app.route('/models', methods=['POST', 'GET'])
@app.route('/models/<model_id>', methods=['GET', 'PUT', 'DELETE'])
def Models(model_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        model_name = request.form["Model Title"].strip()
        fset = m.Featureset.get(m.Featureset.id ==
                                request.form["Select Featureset"])
        model_type = str(request.form['model_type_select'])
        params_to_optimize_list = request.form.getlist("optimize_checkbox")
        model_params = {}
        params_to_optimize = {}
        for k in request.form:
            if k.startswith(model_type + "_"):
                param_name = k.replace(model_type + "_", "")
                if param_name in params_to_optimize_list:
                    params_to_optimize[param_name] = str(request.form[k])
                else:
                    model_params[param_name] = str(request.form[k])
        model_params = {k: csutil.robust_literal_eval(v)
                        for k, v in model_params.items()}
        params_to_optimize = {k: csutil.robust_literal_eval(v)
                              for k, v in params_to_optimize.items()}
        csutil.check_model_param_types(model_type, model_params)
        csutil.check_model_param_types(model_type, params_to_optimize,
                                       all_as_lists=True)
        model_path = pjoin(cfg['paths']['models_folder'],
                           '{}_model.nc'.format(uuid.uuid4()))
        model_file = m.Model.create(uri=model_path)
        model = m.Model(name=model_name, file=model_file, featureset=fset,
                        project=featureset.project, params=model_params,
                        type=model_type)
        build_model_task.delay(model_path, model_type, model_params,
                               fset.file.uri, params_to_optimize)
        return to_json({"status": "success"})
    elif request.method == 'GET':
        if model_id is not None:
            model_info = m.Model.get(m.Model.id == model_id)
        else:
            model_info = [model for p in m.Project.all(USERNAME)
                          for model in p.models]
        return to_json(
            {
                "status": "success",
                "data": model_info
            })
    elif request.method == 'DELETE':
        if model_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - model set ID not provided."
                })
        f = m.Model.get(m.Model.id == model_id)
        if f.is_owned_by(USERNAME):
            f.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return to_json({"status": "success"})
    elif request.method == 'PUT':
        if model_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - model set ID not provided."
                })
        # TODO!
        return to_json(
            {
                "status": "error",
                "message": "Functionality for this endpoint is not yet implemented."
            })


@app.route('/predictions', methods=['POST', 'GET'])
@app.route('/predictions/<prediction_id>', methods=['GET', 'PUT', 'DELETE'])
def Predictions(prediction_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        dataset = m.Dataset.get(m.Dataset.id == int(request.form["Select Dataset"]))
        model = m.Model.get(m.Model.id == request.form["Select Model"])
        fset = model.featureset
        prediction_path = pjoin(cfg['paths']['predictions_folder'],
                                '{}_prediction.nc'.format(uuid.uuid4()))
        prediction_file = m.Prediction.create(uri=prediction_path)
        prediction = m.Prediction(file=prediction_file, dataset=dataset,
                                  project=dataset.project, model=model)
        predict_task(dataset.uris, prediction_path, model.file.uri,
                     custom_features_script=fset.custom_features_script)
        return to_json({"status": "success"})
    elif request.method == 'GET':
        if prediction_id is not None:
            prediction_info = m.Prediction.get(m.Prediction.id == prediction_id)
        else:
            prediction_info = [prediction for p in m.Project.all(USERNAME)
                          for prediction in p.predictions]
        return to_json(
            {
                "status": "success",
                "data": prediction_info
            })
    elif request.method == 'DELETE':
        if prediction_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - prediction set ID not provided."
                })
        f = m.Prediction.get(m.Prediction.id == prediction_id)
        if f.is_owned_by(USERNAME):
            f.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return to_json({"status": "success"})
    elif request.method == 'PUT':
        if prediction_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - prediction set ID not provided."
                })
        # TODO!
        return to_json(
            {
                "status": "error",
                "message": "Functionality for this endpoint is not yet implemented."
            })


@app.route("/features_list", methods=["GET"])
def get_features_list():
    if request.method == "GET":
        return to_json({
            "status": "success",
            "data": {
                "obs_features": oft.FEATURES_LIST,
                "sci_features": sft.FEATURES_LIST},
            "message": None})


# !!!
# This API call should **only be callable by logged in users**
# !!!
@app.route('/socket_auth_token', methods=['GET'])
def socket_auth_token():
    secret = cfg['flask']['secret-key']
    token = jwt.encode({
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'username': get_username()
        }, secret)
    return to_json({'status': 'OK',
                    'data': {'token': token}})
