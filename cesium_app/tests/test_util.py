from cesium_app import util
from cesium_app.ext import sklearn_models
import numpy.testing as npt
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
    """Test sklearn_models.check_model_param_types"""
    model_type = "RandomForestClassifier"
    params = {"n_estimators": 1000,
              "max_features": "auto",
              "min_weight_fraction_leaf": 0.34,
              "bootstrap": True,
              "class_weight": {'a': 0.2, 'b': 0.8}}
    sklearn_models.check_model_param_types(model_type, params)

    params = {"n_estimators": 100.1}
    pytest.raises(ValueError, sklearn_models.check_model_param_types,
                  model_type, params)

    model_type = "RandomForestClassifier"
    params = {"max_features": 150}
    sklearn_models.check_model_param_types(model_type, params)

    model_type = "RandomForestClassifier"
    params = {"max_features": [100, 150, 200],
              "n_estimators": [10, 50, 100, 1000],
              "bootstrap": True}
    normal, opt = sklearn_models.check_model_param_types(model_type, params)
    assert normal == {"bootstrap": True}
    assert opt == {"max_features": [100, 150, 200],
                   "n_estimators": [10, 50, 100, 1000]}

    params = {"max_depth": 100.1}
    pytest.raises(ValueError, sklearn_models.check_model_param_types,
                  model_type, params)

    model_type = "RandomForestClassifier"
    params = {"max_features": 150.3}
    sklearn_models.check_model_param_types(model_type, params)

    params = {"max_depth": False}
    pytest.raises(ValueError, sklearn_models.check_model_param_types,
                  model_type, params)

    model_type = "LinearSGDClassifier"
    params = {"class_weight": {'a': 0.2, 'b': 0.8},
                "average": False}
    sklearn_models.check_model_param_types(model_type, params)

    params = {"average": 20.3}
    pytest.raises(ValueError, sklearn_models.check_model_param_types,
                  model_type, params)

    model_type = "LinearSGDClassifier"
    params = {"class_weight": "some_str",
                "average": 2}
    sklearn_models.check_model_param_types(model_type, params)

    model_type = "RidgeClassifierCV"
    params = {"alphas": [0.1, 2.1, 6.2]}
    sklearn_models.check_model_param_types(model_type, params)

    model_type = "RandomForestClassifier"
    params = {"invalid_param_name": "some_value"}
    pytest.raises(ValueError, sklearn_models.check_model_param_types,
                  model_type, params)
