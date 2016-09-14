from ..util import make_list


model_descriptions = [
    {"name": "RandomForestClassifier",
     "params": [
         {"name": "n_estimators", "type": int, "default": 10},
         {"name": "criterion", "type": str, "default": "gini"},
         {"name": "max_features", "type": [int, float, str],
          "default": "auto"},
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

    {"name": "RandomForestRegressor",
     "params": [
         {"name": "n_estimators", "type": int, "default": 10},
         {"name": "criterion", "type": str, "default": "mse"},
         {"name": "max_features", "type": [int, float, str],
          "default": "auto"},
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
         {"name": "n_iter", "type": int, "default": 5},
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


def check_model_param_types(model_type, model_params, all_as_lists=False):
    """Cast model parameter strings to expected types.

    .. warning:: Modifies `model_params` dict in place.

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

    Raises
    ------
    ValueError
        Raises ValueError if parameter(s) are not of expected type.

    """
    try:
        model_desc = next(md for md in model_descriptions
                              if md['name'] == model_type)
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
        values = value if isinstance(value, list) else [value]

        none_vals = [None, "None", ""]
        values = [None if v in none_vals else v for v in values]

        vtypes = set(make_list(vtype))

        # ints are acceptable values for float parameters
        if float in vtypes:
            vtypes.add(int)

        if not all((type(v) in vtypes) or (v is None) for v in values):
            raise TypeError('Value type does not match specification')


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
        except TypeError as e:
            raise ValueError(
                "Parameter {} in model {} has wrong type"
                .format(param_name, model_desc["name"]))
