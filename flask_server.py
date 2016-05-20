#!/usr/bin/python

import sys
import os
import json
import rethinkdb as rdb
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
from flask import (
    Flask, request, abort, render_template,
    session, Response, jsonify, g, send_from_directory)

from config import cfg
from cesium import obs_feature_tools as oft
from cesium import science_feature_tools as sft
from cesium import data_management
from cesium import time_series as tslib
from cesium import transformation
from cesium import featurize
from cesium import predict
from cesium import build_model


# Flask initialization
app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root',
                 lambda: app.send_static_file('index.html'))

# RethinkDB config:
RDB_HOST = os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015

CESIUM_DB = "cesium_mock"

if not ('--help' in sys.argv or '--install' in sys.argv):

    try:
        rdb_conn = rdb.connect(host=RDB_HOST, port=RDB_PORT, db=CESIUM_DB)
    except rdb.errors.RqlDriverError as e:
        print(e)
        print('Unable to connect to RethinkDB. '
              'Please ensure that it is running.')
        sys.exit(-1)


@app.before_request
def before_request():
    """Establish connection to RethinkDB DB before each request."""
    try:
        g.rdb_conn = rdb.connect(host=RDB_HOST, port=RDB_PORT, db=CESIUM_DB)
    except RqlDriverError:
        print("No database connection could be established.")
        abort(503, "No database connection could be established.")


@app.teardown_request
def teardown_request(exception):
    """Close connection to RethinkDB DB after each request is completed."""
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass


def db_init(force=False):
    """Initialize RethinkDB tables.

    Create a RethinkDB database whose name is the value of the global
    `CESIUM_DB` defined above, and creates tables within the new DB
    with the names 'projects', 'users', 'datasets', 'features', 'models',
    'userauth' and 'predictions', respectively.

    Parameters
    ----------
    force : boolean, optional
        If True, any pre-existing database associated with this app and
        all its tables will be deleted and replaced by empty tables.
        Defaults to False.

    """
    try:
        connection = rdb.connect(host=RDB_HOST, port=RDB_PORT)
    except RqlDriverError as e:
        print('db_init:', e.message)
        if 'not connect' in e.message:
            print('Launch the database by executing `rethinkdb`.')
        return
    if force:
        try:
            rdb.db_drop(CESIUM_DB).run(connection)
        except:
            pass
    try:
        rdb.db_create(CESIUM_DB).run(connection)
    except RqlRuntimeError as e:
        print('db_init:', e.message)
        print('The table may already exist.  Specify the --force flag '
              'to clear existing data.')
        return
    table_names = ['projects', 'users', 'datasets', 'features',
                   'models', 'userauth', 'predictions']

    db = rdb.db(CESIUM_DB)

    for table_name in table_names:
        print('Creating table', table_name)
        db.table_create(table_name, durability='soft').run(connection)
    connection.close()

    print('Database setup completed.')


def get_all_projkeys():
    """Return all project keys.

    Returns
    -------
    list of str
        A list of project keys (strings).

    """
    return [entry["id"] for entry in rdb.table("projects").run(g.rdb_conn)]


@app.route('/get_list_of_projects', methods=['POST', 'GET'])
def get_list_of_projects():
    """Return list of project names current user can access.

    Called from browser to populate select options.

    Returns
    -------
    flask.Response() object
        Creates flask.Response() object with JSONified dict
        (``{'list':list_of_projects}``).

    """
    if request.method == 'GET':
        return Response(json.dumps(list_projects(auth_only=False,
                                                 name_only=False)),
                        mimetype='application/json',
                        headers={'Cache-Control': 'no-cache',
                                 'Access-Control-Allow-Origin': '*'})


@app.route('/get_state', methods=['GET'])
def get_state():
    """
    """
    if request.method == 'GET':
        state = {}
        state["projectsList"] = list_projects(auth_only=False, name_only=False)
        state["datasetsList"] = list_datasets(auth_only=False)
        state["modelsList"] = list_models(auth_only=False)
        state["predictionsList"] = list_predictions(auth_only=False)
        return Response(json.dumps(state),
                        mimetype='application/json',
                        headers={'Cache-Control': 'no-cache',
                                 'Access-Control-Allow-Origin': '*'})


def list_predictions(
        auth_only=False, by_project=False):
    """Return list of strings describing entries in 'predictions' table.

    Parameters
    ----------
    auth_only : bool, optional
        If True, returns only those entries whose parent projects
        current user is authenticated to access. Defaults to False.
    by_project : str, optional
        Name of project to restrict results to. Defaults to False.

    Returns
    -------
    list of str
        List of dicts describing entries in 'models' table.

    """
    if by_project:
        this_projkey = project_name_to_key(by_project)
        cursor = rdb.table("predictions").filter({"projkey": this_projkey})\
                                         .run(g.rdb_conn)
        return [entry for entry in cusor]
    else:
        authed_proj_keys = (
            get_authed_projkeys() if auth_only else get_all_projkeys())
        if len(authed_proj_keys) == 0:
            return []
        return [entry for this_projkey in authed_proj_keys
                for entry in rdb.table("predictions")
                .filter({"projkey": this_projkey}).run(g.rdb_conn)]


def list_models(auth_only=True, by_project=False):
    """Return list of strings describing entries in 'models' table.

    Parameters
    ----------
    auth_only : bool, optional
        If True, returns only those entries whose parent projects
        current user is authenticated to access. Defaults to True.
    by_project : str, optional
        Must be project name or False. Filters by project. Defaults
        to False.

    Returns
    -------
    list of str
        List of dicts describing entries in 'models' table.

    """
    authed_proj_keys = (
        get_authed_projkeys() if auth_only else get_all_projkeys())

    if by_project:
        this_projkey = project_name_to_key(by_project)

        cursor = rdb.table("models").filter({"projkey": this_projkey})\
                                    .pluck("name", "featureset_name", "created",
                                           "type", "id", "meta_feats",
                                           "projkey")\
                                    .run(g.rdb_conn)
        return [entry for entry in cursor]
    else:
        if len(authed_proj_keys) == 0:
            return []
        return [entry for this_projkey in authed_proj_keys
                for entry in
                rdb.table("models").filter({"projkey": this_projkey})
                .pluck("name", "featureset_name", "created", "type",
                       "id", "meta_feats", "projkey").run(g.rdb_conn)]


def list_datasets(auth_only=True, by_project=False):
    """Return list of strings describing entries in 'datasets' table.

    Parameters
    ----------
    auth_only : bool, optional
        If True, returns only those entries whose parent projects
        current user is authenticated to access. Defaults to True.
    by_project : str, optional
        Project name. Filters by project if not False. Defaults to
        False.

    Returns
    -------
    list of str
        List of dicts describing entries in 'datasets' table.

    """
    authed_proj_keys = (
        get_authed_projkeys() if auth_only else get_all_projkeys())
    if by_project:
        this_projkey = project_name_to_key(by_project)
        cursor = rdb.table("datasets").filter({"projkey": this_projkey})\
                                      .run(g.rdb_conn)
        return [entry for entry in cursor]
    else:
        if len(authed_proj_keys) == 0:
            return []
        return [entry for this_projkey in authed_proj_keys
                for entry in rdb.table("datasets")
                .filter({"projkey": this_projkey}).run(g.rdb_conn)]


def list_projects(auth_only=True, name_only=False):
    """Return list of strings describing entries in 'projects' table.

    Parameters
    ----------
    auth_only : bool, optional
        If True, returns only those projects that the current user is
        authenticated to access, else all projects in table are
        returned. Defaults to True.
    name_only : bool, optional
        If True, includes date & time created, omits if False.
        Defaults to False.

    Returns
    -------
    list of str
        List of strings describing project entries.

    """
    return [entry for entry in rdb.table('projects').run(g.rdb_conn)]


def add_project(name, desc="", addl_authed_users=[], user_email="auto"):
    """Add a new entry to the rethinkDB 'projects' table.

    Parameters
    ----------
    name : str
        New project name.
    desc : str, optional
        Project description. Defaults to an empty strings.
    addl_authed_users : list of str, optional
        List of email addresses (str format) of additional users
        authorized to access this new project. Defaults to empty list.
    user_email : str, optional
        Email of user creating new project. If "auto", user email
        determined by `stormpath.user` thread-local. Defauls to "auto".

    Returns
    -------
    str
        RethinkDB key/ID of newly created project entry.

    """
    if user_email in ["auto", None, "None", "none", "Auto"]:
        user_email = "None" # get_current_userkey()
    if isinstance(addl_authed_users, str):
        if addl_authed_users.strip() in [",", ""]:
            addl_authed_users = []
    new_projkey = rdb.table("projects").insert({
        "name": name,
        "description": desc,
        "created": str(rdb.now().in_timezone('-08:00').run(g.rdb_conn))
    }).run(g.rdb_conn)['generated_keys'][0]
    return new_projkey


def add_dataset(name, projkey):
    """Add a new entry to the rethinkDB 'datasets' table.

    Parameters
    ----------
    name : str
        New dataset name.
    projkey : str
        RethinkDB key/ID of parent project.

    Returns
    -------
    str
        RethinkDB key/ID of newly created dataset entry.

    """
    new_dataset_id = rdb.table('datasets').insert({
        'projkey': projkey,
        'name': name,
        'created': str(rdb.now().in_timezone('-08:00').run(g.rdb_conn)),
    }).run(g.rdb_conn)['generated_keys'][0]
    print("Dataset %s entry added to cesium_app db." % name)
    return new_dataset_id


def set_dataset_filenames(dataset_id, ts_filenames):
    rdb.table('datasets').get(dataset_id).update({'ts_filenames':
                                                  ts_filenames}).run(rdb_conn)


def delete_project_by_key(project_key):
    msg = rdb.table("projects").get(project_key).delete().run(g.rdb_conn)
    return msg


def get_project_details(project_name):
    """Return dict containing project details.

    Parameters
    ----------
    project_name : str
        Name of project.

    Returns
    -------
    dict
        Dictionary with the following key-value pairs:
        "authed_users": a list of emails of authenticated users
        "featuresets": a string of HTML markup of a table describing
            all associated featuresets
        "models": a string of HTML markup of a table describing all
            associated models
        "predictions": a string of HTML markup of a table describing
            all associated predictions
        "created": date/time created
        "description": project description

    """
    # TODO: add following info: associated featuresets, models
    entries = []
    cursor = rdb.table("projects").filter({"name": project_name}).run(g.rdb_conn)
    # TOOD


@app.route('/newProject', methods=['POST'])
def newProject():
    """Handle new project form and creates new RethinkDB entry.

    """
    if request.method == 'POST':
        proj_name = str(request.form["Project Name"]).strip()
        if proj_name == "":
            return jsonify({
                "result": ("Project name must contain at least one "
                           "non-whitespace character. Please try another name.")
            })

        proj_description = str(request.form["Description/notes"]).strip()

        addl_users = str(request.form["Additional Authorized Users"])\
            .strip().split(',')
        if addl_users in [[''], ["None"]]:
            addl_users = []
        if "user_email" in request.form:
            user_email = str(request.form["user_email"]).strip()
        else:
            user_email = "auto"  # will be determined through Flask

        addl_users = [addl_user.strip() for addl_user in addl_users]
        if user_email == "":
            return jsonify({
                "result": ("Required parameter 'user_email' must be a valid "
                           "email address.")})

        new_projkey = add_project(
            proj_name, desc=proj_description, addl_authed_users=addl_users,
            user_email=user_email)
        return Response(json.dumps(list_projects(auth_only=False,
                                                 name_only=False)),
                        mimetype='application/json',
                        headers={'Cache-Control': 'no-cache',
                                 'Access-Control-Allow-Origin': '*'})


@app.route('/deleteProject', methods=['POST'])
def deleteProject():
    """Handle 'deleteProject' form submission.

    Returns
    -------
    JSON response object
        JSONified dict containing result message.

    """
    if request.method == 'POST':
        proj_key = str(request.form["project_key"])

        result = delete_project_by_key(proj_key)
        return Response(json.dumps(list_projects(auth_only=False,
                                                 name_only=False)),
                        mimetype='application/json',
                        headers={'Cache-Control': 'no-cache',
                                 'Access-Control-Allow-Origin': '*'})


@app.route(('/uploadData/<dataset_name>/<headerfile>/<zipfile>/<project_name>'),
           methods=['POST'])
@app.route('/uploadData', methods=['POST'])
def uploadData(dataset_name=None, headerfile=None, zipfile=None, project_name=None):
    """Save uploaded time series data files

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
        dataset_name = str(request.form["Dataset Name"]).strip()
        headerfile = request.files["Header File"]
        zipfile = request.files["Tarball Containing Data"]
        if dataset_name == "":
            return jsonify({
                "message": ("Dataset Title must contain non-whitespace "
                            "characters. Please try a different title."),
                "type": "error"})
        projkey = (request.form["Select Project"])
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
            return jsonify({"message": str(err), "type": "error"})
        except custom_exceptions.TimeSeriesFileNameError as err:
            os.remove(headerfile_path)
            os.remove(zipfile_path)
            print("Removed", headerfile_name, "and", zipfile_name)
            return jsonify({"message": str(err), "type": "error"})
        except:
            raise
        new_dataset_id = add_dataset(name=dataset_name, projkey=projkey)
        time_series = data_management.parse_and_store_ts_data(
            zipfile_path, cfg['paths']['ts_data_folder'], headerfile_path,
            new_dataset_id)
        ts_paths = [ts.path for ts in time_series]
        set_dataset_filenames(new_dataset_id, ts_paths)
        return jsonify({
            "message": "New time series files saved successfully.",
            "dataset_name": dataset_name,
            "headerfile_name": headerfile_name, "zipfile_name": zipfile_name,
            "dataset_id": new_dataset_id,
            "datasetsList": list_datasets(auth_only=False)})


@app.route(('/FeaturizeData/<dataset_id>/<project_name>'
            '/<featureset_name>/<features_to_use>/<custom_features_script>/'
            '<user_email>/<email_user>/<is_test>'), methods=['POST'])
@app.route('/FeaturizeData', methods=['POST', 'GET'])
def FeaturizeData(
        dataset_id=None, project_name=None,
        featureset_name=None, features_to_use=None,
        custom_features_script=None, user_email=None, email_user=False,
        is_test=False):
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
            return jsonify({
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
            email_user = request.form["email_user"]
            if email_user == "True":
                email_user = True
        except:  # unchecked
            email_user = False
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
            email_user=email_user, custom_script_path=customscript_path)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
