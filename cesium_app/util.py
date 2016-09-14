import ast
import hashlib


__all__ = ['make_list', 'robust_literal_eval']


def make_list(x):
    import collections
    if isinstance(x, collections.Iterable) and not isinstance(x, (str, dict)):
        return x
    else:
        return [x]


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
    filename = filename.encode('utf-8')
    return hashlib.sha256(filename).hexdigest()[:20]
