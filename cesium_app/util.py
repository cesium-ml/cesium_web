import ast
import hashlib
import csv


__all__ = ['robust_literal_eval', 'prediction_to_csv']


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


def secure_filename(filename):
    """Create secure file name from SHA-256 hash of `filename`."""
    filename = filename.encode('utf-8')
    return hashlib.sha256(filename).hexdigest()[:20]
