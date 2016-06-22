#!/usr/bin/python

import sys
import os
from os.path import join as pjoin
import tarfile
from json_util import to_json
from flask import (
    Flask, request, abort, render_template,
    session, Response, jsonify, g, send_from_directory)
import uuid
from werkzeug.utils import secure_filename

from config import cfg
from cesium import obs_feature_tools as oft
from cesium import science_feature_tools as sft
from cesium import data_management
from cesium import time_series as tslib
from cesium import transformation
from cesium import featurize
from cesium import predict
from cesium import build_model
from cesium import custom_exceptions

import models as m

# Flask initialization
app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root',
                 lambda: app.send_static_file('index.html'))


# TODO: FIXME!
USERNAME = "testuser@gmail.com" # get_current_userkey()


class UnauthorizedAccess(Exception):
    pass


@app.before_request
def before_request():
    m.db.connect()


@app.after_request
def after_request(response):
    m.db.close()
    return response


@app.route("/project", methods=["GET", "POST"])
@app.route("/project/<project_id>", methods=["GET", "PUT", "DELETE"])
def Project(project_id=None):
    """
    """
    if request.method == 'POST':
        proj_name = str(request.form["Project Name"]).strip()
        proj_description = str(request.form["Description/notes"]).strip()
        try:
            m.Project.add_by(proj_name, proj_description, USERNAME)
        except Exception as e:
            return to_json(
                {
                    "status": "error",
                    "message": str(e)
                })
        return to_json({"status": "success"})

    elif request.method == "GET":
        if project_id is not None:
            proj_info = m.Project.get(m.Project.id == project_id)
        else:
            proj_info = m.Project.all(USERNAME)

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

    elif request.method == "DELETE":
        if project_id is None:
            return to_json(
                {
                    "status": "error",
                    "message": "Invalid request - project ID not provided."
                })
        p = m.Project.get(m.Project.id == project_id)
        if p.is_owned_by(USERNAME):
            p.delete_instance()
        else:
            raise UnauthorizedAccess("User not authorized for project.")

        return to_json({"status": "success"})


@app.route('/get_state', methods=['GET'])
def get_state():
    """
    TODO change to use REST/CRUD
    """
    if request.method == 'GET':
        state = {}
        state["projectsList"] = m.Project.all(USERNAME)
        state["datasetsList"] = [d for p in state["projectsList"]
                                 for d in p.datasets]
        return Response(to_json(state),
                        mimetype='application/json',
                        headers={'Cache-Control': 'no-cache',
                                 'Access-Control-Allow-Origin': '*'})


def set_dataset_filenames(dataset_id, ts_filenames):
    rdb.table('datasets').get(dataset_id).update({'ts_filenames':
                                                  ts_filenames}).run(rdb_conn)


@app.route('/dataset', methods=['POST', 'GET'])
@app.route('/dataset/<dataset_id>', methods=['GET', 'PUT', 'DELETE'])
def Dataset(dataset_id=None):
    """
    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':

        # Parse form fields
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
        try:
            check_headerfile_and_tsdata_format(headerfile_path, zipfile_path)
        except custom_exceptions.DataFormatError as err:
            os.remove(headerfile_path)
            os.remove(zipfile_path)
            print("Removed", headerfile_name, "and", zipfile_name)
            return to_json({"message": str(err), "status": "error"})
        except custom_exceptions.TimeSeriesFileNameError as err:
            os.remove(headerfile_path)
            os.remove(zipfile_path)
            print("Removed", headerfile_name, "and", zipfile_name)
            return to_json({"message": str(err), "status": "error"})
        except:
            raise

        p = m.Project.get(m.Project.id == project_id)
        time_series = data_management.parse_and_store_ts_data(zipfile_path,
            cfg['paths']['ts_data_folder'], headerfile_path)
        ts_paths = [ts.path for ts in time_series]
        d = m.Dataset.add(name=dataset_name, project=p, ts_paths=ts_paths)

        return to_json({"status": "success"})
    elif request.method == "GET":
        if dataset_id is not None:
            dataset_info = m.Dataset.get(m.Dataset.id == dataset_id)
        else:
            dataset_info = [d for p in m.Project.all(USERNAME)
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
        if d.is_owned_by(USERNAME):
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
                "message": "Functionality for this endpoint is not yet implemented."
            })


@app.route(('/FeaturizeData/<dataset_id>/<project_name>'
            '/<featureset_name>/<features_to_use>/<custom_features_script>/'
            '<is_test>'), methods=['POST'])
@app.route('/FeaturizeData', methods=['POST', 'GET'])
def FeaturizeData(
        dataset_id=None, project_name=None,
        featureset_name=None, features_to_use=None,
        custom_features_script=None, is_test=False):
    """Save uploaded time series data files and begin featurization.

    Handles POST form submission.

    Returns
    -------
    Redirects to featurizationPage, see that function for output
    details.

    """
    # TODO: ADD MORE ROBUST EXCEPTION HANDLING (HERE AND ALL OTHER FUNCTIONS)
    if request.method == 'POST':
        post_method = "browser"
        # Parse form fields
        featureset_name = str(request.form["featureset_name"]).strip()
        if featureset_name == "":
            return to_json({
                "message": ("Feature Set Title must contain non-whitespace "
                            "characters. Please try a different title."),
                "type": "error"})
        dataset_id = str(request.form["featureset_dataset_select"]).strip()
        project_name = (str(request.form["featureset_project_name_select"]).
                        strip().split(" (created")[0])
        features_to_use = request.form.getlist("features_selected")
        custom_script_tested = str(request.form["custom_script_tested"])
        if custom_script_tested == "yes":
            custom_script = request.files["custom_feat_script_file"]
            customscript_fname = str(secure_filename(custom_script.filename))
            print(customscript_fname, 'uploaded.')
            customscript_path = pjoin(
                    cfg['paths']['upload_folder'], "custom_feature_scripts",
                    str(uuid.uuid4()) + "_" + str(customscript_fname))
            custom_script.save(customscript_path)
            custom_features = request.form.getlist("custom_feature_checkbox")
            features_to_use += custom_features
        else:
            customscript_path = False
        print("Selected features:", features_to_use)
        try:
            is_test = request.form["is_test"]
            if is_test == "True":
                is_test = True
        except:  # unchecked
            is_test = False
        proj_key = project_name_to_key(project_name)
        return featurizationPage(
            featureset_name=featureset_name, project_name=project_name,
            dataset_id=dataset_id,
            featlist=features_to_use, is_test=is_test,
            custom_script_path=customscript_path)


def check_headerfile_and_tsdata_format(headerfile_path, zipfile_path):
    """Ensure uploaded files are correctly formatted.

    Ensures that headerfile_path and zipfile_path conform
    to expected format - returns False if so, raises Exception if not.

    Parameters
    ----------
    headerfile_path : str
        Path to header file to inspect.
    zipfile_path : str
        Path to tarball to inspect.

    Returns
    -------
    bool
        Returns False if files are correctly formatted, otherwise
        raises an exception (see below).

    Raises
    ------
    custom_exceptions.TimeSeriesFileNameError
        If any provided time-series data files' names are absent in
        provided header file.
    custom_exceptions.DataFormatError
        If provided time-series data files or header file are
        improperly formatted.

    """
    with open(headerfile_path) as f:
        all_header_fnames = []
        column_header_line = str(f.readline())
        for line in f:
            line = str(line)
            if line.strip() != '':
                if len(line.strip().split(",")) < 2:
                    raise custom_exceptions.DataFormatError((
                        "Header file improperly formatted. At least two "
                        "comma-separated columns (file_name,class_name) are "
                        "required."))
                else:
                    all_header_fnames.append(line.strip().split(",")[0])
    the_zipfile = tarfile.open(zipfile_path)
    file_list = list(the_zipfile.getnames())
    all_fname_variants = []
    for file_name in file_list:
        this_file = the_zipfile.getmember(file_name)
        if this_file.isfile():
            file_name_variants = list_filename_variants(file_name)
            all_fname_variants.extend(file_name_variants)
            if (len(list(set(file_name_variants) &
                         set(all_header_fnames))) == 0):
                raise custom_exceptions.TimeSeriesFileNameError((
                    "Time series data file %s provided in tarball/zip file "
                    "has no corresponding entry in header file.")
                    % str(file_name))
            f = the_zipfile.extractfile(this_file)
            all_lines = [
                line.strip() for line in f.readlines() if line.strip() != '']
            line_no = 1
            for line in all_lines:
                line = str(line)
                if line_no == 1:
                    num_labels = len(line.split(','))
                    if num_labels < 2:
                        raise custom_exceptions.DataFormatError((
                            "Time series data file improperly formatted; at "
                            "least two comma-separated columns "
                            "(time,measurement) are required. Error occurred "
                            "on file %s") % str(file_name))
                else:
                    if len(line.split(',')) != num_labels:
                        raise custom_exceptions.DataFormatError((
                            "Time series data file improperly formatted; in "
                            "file %s line number %s has %s columns while the "
                            "first line has %s columns.") %
                            (
                                file_name, str(line_no),
                                str(len(line.split(","))), str(num_labels)))
                line_no += 1
    for header_fname in all_header_fnames:
        if header_fname not in all_fname_variants:
            raise custom_exceptions.TimeSeriesFileNameError((
                "Header file entry with file_name=%s has no corresponding "
                "file in provided tarball/zip file.") % header_fname)
    return False


def list_filename_variants(file_name):
    """Return list of possible matching file name variants.
    """
    return [file_name, os.path.basename(file_name),
            os.path.splitext(file_name)[0],
            os.path.splitext(os.path.basename(file_name))[0]]


@app.route("/get_features_list", methods=["GET"])
def get_features_list():
    if request.method == "GET":
        return to_json({
            "status": "success",
            "data": {
                "obs_features": oft.FEATURES_LIST,
                "sci_features": sft.FEATURES_LIST},
            "message": None})


if __name__ == '__main__':
    app.run(debug=True, port=4000)
