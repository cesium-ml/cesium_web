'''Assortment of utility functions.'''

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
    """Create secure file name from SHA-256 has of `filename`."""
    filename = filename.encode('utf-8')
    return hashlib.sha256(filename).hexdigest()[:20]


def prediction_to_csv(pred, outpath=None):
    """Convert an `xarray.Dataset` prediction object's results to CSV.

    Parameters
    ----------
    pred : `xarray.Dataset`
        The `xarray.Dataset` object containing prediction data.
    outpath : str, optional
        Path to save CSV, if desired. Defaults to None.

    Returns
    -------
    list of lists of str (if `outpath` is None) or str
        If `outpath` is not None, returns a list of lists representing the
        tabular form of the prediction results, e.g.
        [['ts_name', 'target', 'prediction'],
         ['ts_1', 'Class_A', 'Class_A']]
        If `outpath` is specified, the data is saved in CSV format to the
        path specified, which is then returned.

    """
    head = ['ts_name']
    rows = []

    first_iter = True

    for tsname in pred.name.values:
        entry = pred.sel(name=tsname)
        row = [tsname]

        if 'target' in entry:
            row.append(entry.target.values.item())

            if first_iter:
                head.append('true_target')

        if 'class_label' in entry:
            for label, val in zip(entry.class_label.values,
                                  entry.prediction.values):
                row.extend([str(label), str(val)])

                if first_iter:
                    head.extend(['predicted_class', 'probability'])
        else:
            row.append(str(entry.prediction.values.item()))

            if first_iter:
                head.extend(['prediction'])

        rows.append(row)
        first_iter = False

    all_rows = [head]
    all_rows.extend(rows)

    if outpath:
        with open(outpath, 'w') as f:
            csv.writer(f).writerows(all_rows)
        return outpath
    else:
        return all_rows
