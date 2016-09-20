import ast
import hashlib
import csv


__all__ = ['make_list', 'robust_literal_eval', 'prediction_to_csv']


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


def prediction_to_csv(pred, outpath=None):
    head = ['ts_name']
    els = []
    first_iter = True
    for tsname in pred.name.values:
        els.append([tsname])
        entry = pred.sel(name=tsname)
        if 'target' in entry:
            els[-1].append(entry.target.values.item())
            if first_iter:
                head.append('true_target')
        if 'class_label' in entry:
            for label, val in zip(entry.class_label.values,
                                  entry.prediction.values):
                els[-1].extend([str(label), str(val)])
                if first_iter:
                    head.extend(['predicted_class', 'probability'])
        else:
            els[-1].append(str(entry.prediction.values.item()))
            if first_iter:
                head.extend(['prediction'])
        els[-1][-1] += '\n'
        first_iter = False

    head[-1] += '\n'
    all_rows = [head]
    all_rows.extend(els)
    if outpath:
        with open(outpath, 'w') as f:
            csv.writer(f).writerows(all_rows)
        return outpath
    else:
        return all_rows
