import ast
import contextlib
import errno
import os
import subprocess
import tarfile
import tempfile
import zipfile

import numpy as np
import requests

from .ext.sklearn_models import model_descriptions


__all__ = ['check_model_param_types', 'make_list',
           'robust_literal_eval', 'warn_defaultdict']


def make_list(x):
    import collections
    if isinstance(x, collections.Iterable) and not isinstance(x, (str, dict)):
        return x
    else:
        return [x,]


def check_model_param_types(model_type, model_params, all_as_lists=False):
    """Cast model parameter strings to expected types.

    Modifies `model_params` dict in place.

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


def robust_literal_eval(val):
    """Call `ast.literal_eval` without raising `ValueError`.

    Parameters
    ----------
    val : str
        String literal to be evaluated.

    Returns
    -------
    Output of `ast.literal_eval(val)', or `val` if `ValueError` was raised.

    """
    try:
        return ast.literal_eval(val)
    except ValueError:
        return val
