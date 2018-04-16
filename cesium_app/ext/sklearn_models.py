import collections
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import (LinearRegression, SGDClassifier,
                                  RidgeClassifierCV, ARDRegression,
                                  BayesianRidge)

MODELS_TYPE_DICT = {'RandomForestClassifier': RandomForestClassifier,
                    'RandomForestRegressor': RandomForestRegressor,
                    'LinearSGDClassifier': SGDClassifier,
                    'LinearRegressor': LinearRegression,
                    'RidgeClassifierCV': RidgeClassifierCV,
                    'BayesianARDRegressor': ARDRegression,
                    'BayesianRidgeRegressor': BayesianRidge}


def make_list(x):
    """Wrap `x` in a list if it isn't already a list or tuple.

    Parameters
    ----------
    x : any valid object
        The parameter to be wrapped in a list.

    Returns
    -------
    list or tuple
        Returns `[x]` if `x` is not already a list or tuple, otherwise
        returns `x`.

    """
    if isinstance(x, collections.Iterable) and not isinstance(x, (str, dict)):
        return x
    else:
        return [x]


model_descriptions = [
    {"name": "RandomForestClassifier (fast)",
     "params": [
         {"name": "n_estimators", "type": int, "default": 50},
         {"name": "criterion", "type": str, "default": ["gini", "entropy"]},
         {"name": "max_features", "type": [int, float, str],
          "default": [0.05, 0.1, 0.15, 0.2]},
         {"name": "max_depth", "type": int, "default": None},
         {"name": "min_samples_split", "type": int, "default": 2},
         {"name": "min_samples_leaf", "type": int, "default": 1},
         {"name": "min_weight_fraction_leaf", "type": float, "default": 0.},
         {"name": "max_leaf_nodes", "type": int, "default": None},
         {"name": "bootstrap", "type": bool, "default": True},
         {"name": "oob_score", "type": bool, "default": False},
         {"name": "random_state", "type": int, "default": None},
         {"name": "class_weight", "type": dict, "default": None}],
     "type": "classifier",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html"},

    {"name": "RandomForestClassifier (comprehensive)",
     "params": [
         {"name": "n_estimators", "type": int, "default": [100, 250]},
         {"name": "criterion", "type": str, "default": ["gini", "entropy"]},
         {"name": "max_features", "type": [int, float, str],
          "default": [0.05, 0.085, 0.1, 0.15, 0.13, 0.15, 0.2, 0.25]},
         {"name": "max_depth", "type": int, "default": None},
         {"name": "min_samples_split", "type": int, "default": 2},
         {"name": "min_samples_leaf", "type": int, "default": [1, 2, 5]},
         {"name": "min_weight_fraction_leaf", "type": float, "default": 0.},
         {"name": "max_leaf_nodes", "type": int, "default": None},
         {"name": "bootstrap", "type": bool, "default": True},
         {"name": "oob_score", "type": bool, "default": False},
         {"name": "random_state", "type": int, "default": None},
         {"name": "class_weight", "type": dict, "default": None}],
     "type": "classifier",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html"},

    {"name": "RandomForestRegressor (fast)",
     "params": [
         {"name": "n_estimators", "type": int, "default": 50},
         {"name": "criterion", "type": str, "default": "mse"},
         {"name": "max_features", "type": [int, float, str],
          "default": [0.28, 0.33, 0.38]},
         {"name": "max_depth", "type": int, "default": None},
         {"name": "min_samples_split", "type": int, "default": 2},
         {"name": "min_samples_leaf", "type": int, "default": 1},
         {"name": "min_weight_fraction_leaf", "type": float, "default": 0.},
         {"name": "max_leaf_nodes", "type": int, "default": None},
         {"name": "bootstrap", "type": bool, "default": True},
         {"name": "oob_score", "type": bool, "default": False},
         {"name": "random_state", "type": int, "default": None}],
     "type": "regressor",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html"},

    {"name": "RandomForestRegressor (comprehensive)",
     "params": [
         {"name": "n_estimators", "type": int, "default": [100, 250]},
         {"name": "criterion", "type": str, "default": ["mse", "mae"]},
         {"name": "max_features", "type": [int, float, str],
          "default": [0.165, 0.28, 0.33, 0.38, 0.43, 0.5, 0.667]},
         {"name": "max_depth", "type": int, "default": None},
         {"name": "min_samples_split", "type": int, "default": 2},
         {"name": "min_samples_leaf", "type": int, "default": 1},
         {"name": "min_weight_fraction_leaf", "type": float, "default": 0.},
         {"name": "max_leaf_nodes", "type": int, "default": None},
         {"name": "bootstrap", "type": bool, "default": True},
         {"name": "oob_score", "type": bool, "default": False},
         {"name": "random_state", "type": int, "default": None}],
     "type": "regressor",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html"},


    {"name": "LinearSGDClassifier",
     "params": [
         {"name": "loss", "type": str, "default": "hinge"},
         {"name": "penalty", "type": str, "default": "l2"},
         {"name": "alpha", "type": float, "default": 0.0001},
         {"name": "l1_ratio", "type": float, "default": 0.15},
         {"name": "fit_intercept", "type": bool, "default": True},
         {"name": "max_iter", "type": int, "default": None},
         {"name": "tol", "type": float, "default": None},
         {"name": "shuffle", "type": bool, "default": True},
         {"name": "random_state", "type": int, "default": None},
         {"name": "epsilon", "type": float, "default": 0.1},
         {"name": "learning_rate", "type": str, "default": "optimal"},
         {"name": "eta0", "type": float, "default": 0.0},
         {"name": "power_t", "type": float, "default": 0.5},
         {"name": "class_weight", "type": [dict, str], "default": None},
         {"name": "average", "type": [bool, int], "default": False}],
     "type": "classifier",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html"},

    {"name": "LinearRegressor",
     "params": [
         {"name": "fit_intercept", "type": bool, "default": True},
         {"name": "normalize", "type": bool, "default": False}],
     "type": "regressor",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html"},

    {"name": "RidgeClassifierCV",
     "params": [
         {"name": "alphas", "type": list,
          "default": [0.1, 1., 10.]},
         {"name": "fit_intercept", "type": bool, "default": True},
         {"name": "normalize", "type": bool, "default": False},
         {"name": "scoring", "type": str, "default": None},
         {"name": "cv", "type": "generator", "default": None},
         {"name": "class_weight", "type": dict, "default": None}],
     "type": "classifier",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RidgeClassifierCV.html"},

    {"name": "BayesianARDRegressor",
     "params": [
         {"name": "n_inter", "type": int, "default": 300},
         {"name": "tol", "type": float, "default": 0.001},
         {"name": "alpha_1", "type": float, "default": 1.e-06},
         {"name": "alpha_2", "type": float, "default": 1.e-06},
         {"name": "lambda_1", "type": float, "default": 1.e-06},
         {"name": "lambda_2", "type": float, "default": 1.e-06},
         {"name": "compute_score", "type": bool, "default": False},
         {"name": "threshold_lambda", "type": float, "default": 10000.},
         {"name": "fit_intercept", "type": bool, "default": True},
         {"name": "normalize", "type": bool, "default": False}],
     "type": "regressor",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ARDRegression.html"},

    {"name": "BayesianRidgeRegressor",
     "params": [
         {"name": "n_iter", "type": int, "default": 300},
         {"name": "tol", "type": float, "default": 0.001},
         {"name": "alpha_1", "type": float, "default": 1.e-06},
         {"name": "alpha_2", "type": float, "default": 1.e-06},
         {"name": "lambda_1", "type": float, "default": 1.e-06},
         {"name": "lambda_2", "type": float, "default": 1.e-06},
         {"name": "compute_score", "type": bool, "default": False},
         {"name": "fit_intercept", "type": bool, "default": True},
         {"name": "normalize", "type": bool, "default": False}],
     "type": "regressor",
     "url": "http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.BayesianRidge.html"}]

for model_dict in model_descriptions:
    model_dict['description'] = (MODELS_TYPE_DICT[model_dict['name'].split()[0]]
                                 .__doc__.split('\n')[0].strip())
    if '(fast)' in model_dict['name']:
        model_dict['description'] += (' (Optimized over a smaller number of '
                                      'possible parameter values.)')
    elif '(comprehensive)' in model_dict['name']:
        model_dict['description'] += (' (Optimized over a larger number of '
                                      'possible parameter values.)')


def check_model_param_types(model_type, model_params, all_as_lists=False):
    """Ensure parameters are of expected type; split standard values and grids.

    Parameters
    ----------
    model_type : str
        Name of model.
    model_params : dict
        Dictionary containing model parameters to be checked against expected
        types.
    all_as_lists : bool, optional
        Boolean indicating whether `model_params` values are wrapped in lists,
        as in the case of parameter grids for optimization.

    Returns
    -------
    (dict, dict) tuple
        Returns a tuple of two dictionaries, the first of which contains those
        hyper-parameters that are to be passed into the model constructor as-is,
        and the second containing hyper-parameter grids intended for
        optimization (with GridSearchCV).

    Raises
    ------
    ValueError
        Raises ValueError if parameter(s) are not of expected type.

    """
    try:
        model_desc = next(md for md in model_descriptions
                          if model_type in [md['name'], md['name'].split()[0]])
    except StopIteration:
        raise ValueError("model_type not in list of allowable models.")


    def verify_type(value, vtype):
        """Ensure that value is of vtype.

        Parameters
        ----------
        value : any
            Input value.
        vtype : type or list of types
            Check that value is one of these types.

        """
        vtypes = set(make_list(vtype))
        # Ensure that `values` is a list of parameter values
        values = make_list(value) if list not in vtypes else [value]

        none_vals = [None, "None", ""]
        values = [None if v in none_vals else v for v in values]

        vtypes = set(make_list(vtype))

        # ints are acceptable values for float parameters
        if float in vtypes:
            vtypes.add(int)

        if not all((type(v) in vtypes) or (v is None) for v in values):
            raise TypeError('Value type does not match specification')


    standard_params = {}
    params_to_optimize = {}

    # Iterate through params and check against specification
    for param_name, param_value in model_params.items():
        try:
            required_type = next(param_desc["type"]
                                     for param_desc in model_desc["params"]
                                     if param_desc["name"] == param_name)
        except StopIteration:
            raise ValueError("Unknown parameter {} found in model {}".format(
                param_name, model_desc["name"]))

        try:
            verify_type(param_value, required_type)
            if (make_list(param_value) == param_value and list not in
                set(make_list(required_type))):
                params_to_optimize[param_name] = param_value
            else:
                standard_params[param_name] = param_value
        except TypeError as e:
            raise ValueError(
                "Parameter {} in model {} has wrong type. Expected {} and got "
                "{} (type {})."
                .format(param_name, model_desc["name"], required_type,
                        param_value, type(param_value)))

    return standard_params, params_to_optimize
