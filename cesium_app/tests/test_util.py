import os
from cesium_app import util
from cesium_app.ext.sklearn_models import model_descriptions
import numpy.testing as npt
try:
    import docker
    dockerpy_installed = True
except ImportError:
    dockerpy_installed = False
import pytest


def test_robust_literal_eval():
    """Test util.robust_literal_eval"""
    params = {"n_estimators": "1000",
              "max_features": "auto",
              "min_weight_fraction_leaf": "0.34",
              "bootstrap": "True",
              "class_weight": "{'a': 0.2, 'b': 0.8}",
              "max_features2": "[150.3, 20, 'auto']"}
    expected = {"n_estimators": 1000,
                "max_features": "auto",
                "min_weight_fraction_leaf": 0.34,
                "bootstrap": True,
                "class_weight": {'a': 0.2, 'b': 0.8},
                "max_features2": [150.3, 20, "auto"]}
    params = {k: util.robust_literal_eval(v) for k, v in params.items()}
    npt.assert_equal(params, expected)


def test_check_model_param_types():
    """Test util.check_model_param_types"""
    model_type = "RandomForestClassifier"
    params = {"n_estimators": 1000,
                "max_features": "auto",
                "min_weight_fraction_leaf": 0.34,
                "bootstrap": True,
                "class_weight": {'a': 0.2, 'b': 0.8}}
    util.check_model_param_types(model_type, params)

    params = {"n_estimators": 100.1}
    pytest.raises(ValueError, util.check_model_param_types, model_type, params)

    model_type = "RandomForestClassifier"
    params = {"max_features": 150}
    util.check_model_param_types(model_type, params)

    params = {"max_depth": 100.1}
    pytest.raises(ValueError, util.check_model_param_types, model_type, params)

    model_type = "RandomForestClassifier"
    params = {"max_features": 150.3}
    util.check_model_param_types(model_type, params)

    params = {"max_depth": False}
    pytest.raises(ValueError, util.check_model_param_types, model_type, params)

    model_type = "LinearSGDClassifier"
    params = {"class_weight": {'a': 0.2, 'b': 0.8},
                "average": False}
    util.check_model_param_types(model_type, params)

    params = {"average": 20.3}
    pytest.raises(ValueError, util.check_model_param_types, model_type, params)

    model_type = "LinearSGDClassifier"
    params = {"class_weight": "some_str",
                "average": 2}
    util.check_model_param_types(model_type, params)

    model_type = "RidgeClassifierCV"
    params = {"alphas": [[0.1, 2.1, 6.2]]}
    util.check_model_param_types(model_type, params)

    # Test parameter grid for optimization input
    model_type = "RandomForestClassifier"
    params_to_optimize = {"max_features": [150.3, 20, "auto"]}
    util.check_model_param_types(model_type, params_to_optimize,
                                 all_as_lists=True)

    params_to_optimize = {"n_estimators": [20.3, 15.2]}
    pytest.raises(ValueError, util.check_model_param_types, model_type,
                  params_to_optimize, all_as_lists=True)

    model_type = "RandomForestClassifier"
    params = {"invalid_param_name": "some_value"}
    pytest.raises(ValueError, util.check_model_param_types, model_type, params)


def test_make_list():
    """Test util.make_list"""
    npt.assert_equal(util.make_list(1), [1])
    npt.assert_equal(util.make_list([1]), [1])
