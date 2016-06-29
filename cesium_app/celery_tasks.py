from cesium import featurize, build_model, predict
from .celery_app import app
from . import models as m


@app.task()
def featurize_task(ts_paths, output_path, features_to_use,
                   custom_script_path=None, is_test=False):
    """TODO

    Parameters
    ----------
    headerfile_path : str
        Path to TS data header file.
    zipfile_path : str
        Path TS data tarball.
    features_to_use : list
        List of features to generate.
    featureset_key : str
        RethinkDB ID of new feature set.
    is_test : bool
        Boolean indicating whether to run as test.
    custom_script_path : str
        Path to custom features definition script, or "None".
    """
    first_N = cfg['cesium']['TEST_N'] if is_test else None
    featurize.featurize_data_files(ts_paths, features_to_use=features_to_use,
                                   output_path=output_path, first_N=first_N,
                                   custom_script_path=custom_script_path)
    # TODO send websocket message after completion


@app.task()
def build_model_task(output_path, model_type, model_params, fset_path,
                     params_to_optimize=None):
    """Build a model based on given features.

    Parameters
    ----------
    model_type : str
        Abbreviation of the model type to be created (e.g. "RFC").
    model_params : dict
        Dictionary specifying sklearn model parameters to be used.
    model_key : str
        Key/ID associated with model.
    params_to_optimize : list of str, optional
        List of parameter names that are formatted for hyperparameter
        optimization.

    Returns
    -------
    bool
        Returns True.

    """
    with xr.open_dataset(fset_path) as fset:
        build_model.create_and_pickle_model(fset, model_type=model_type,
                                            output_path=model_path,
                                            model_options=model_params,
                                            params_to_optimize=params_to_optimize)
    # TODO send websocket message after completion


@app.task()
def predict_task(ts_paths, output_path, model_path, custom_features_script=None):
    """TODO

    Parameters
    ----------
    headerfile_path : str
        Path to TS data header file.
    zipfile_path : str
        Path TS data tarball.
    features_to_use : list
        List of features to generate.
    featureset_key : str
        RethinkDB ID of new feature set.
    is_test : bool
        Boolean indicating whether to run as test.
    custom_script_path : str
        Path to custom features definition script, or "None".
    """
    predict.predict_data_files(ts_paths, features_to_use, model, output_path,
                               custom_features_script)
    # TODO send websocket message after completion
