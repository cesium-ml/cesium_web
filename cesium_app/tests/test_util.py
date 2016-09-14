from cesium_app import util
import numpy.testing as npt


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


def test_make_list():
    """Test util.make_list"""
    npt.assert_equal(util.make_list(1), [1])
    npt.assert_equal(util.make_list([1]), [1])
