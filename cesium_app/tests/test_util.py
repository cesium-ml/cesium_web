from cesium_app import util
from cesium_app.ext import sklearn_models
import numpy.testing as npt
import pytest
import xarray as xr
from cesium_app.tests.fixtures import (create_test_project, create_test_dataset,
                                       create_test_featureset, create_test_model,
                                       create_test_prediction)


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


def test_prediction_to_csv_class():
    """Test util.prediction_to_csv"""
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs,\
         create_test_model(fs, model_type='LinearSGDClassifier') as m,\
         create_test_prediction(ds, m) as pred:
        pred = xr.open_dataset(pred.file.uri)
        assert util.prediction_to_csv(pred) ==\
            [['ts_name', 'true_target', 'prediction'],
             ['0', 'Mira', 'Mira'],
             ['1', 'Classical_Cepheid', 'Classical_Cepheid'],
             ['2', 'Mira', 'Mira'],
             ['3', 'Classical_Cepheid', 'Classical_Cepheid'],
             ['4', 'Mira', 'Mira']]


def test_prediction_to_csv_regr():
    """Test util.prediction_to_csv"""
    with create_test_project() as p, create_test_dataset(p, label_type='regr') as ds,\
         create_test_featureset(p, label_type='regr') as fs,\
         create_test_model(fs, model_type='LinearRegressor') as m,\
         create_test_prediction(ds, m) as pred:

        pred = xr.open_dataset(pred.file.uri)
        results = util.prediction_to_csv(pred)

        assert results[0] == ['ts_name', 'true_target', 'prediction']

        npt.assert_array_almost_equal(
            [[float(e) for e in row] for row in results[1:]],
            [[0, 2.2, 2.2],
             [1, 3.4, 3.4],
             [2, 4.4, 4.4],
             [3, 2.2, 2.2],
             [4, 3.1, 3.1]])
