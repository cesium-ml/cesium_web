from datetime import datetime
import json
import numpy as np
import peewee
import six
import xarray as xr


data_types = {
    int: 'int',
    float: 'float',
    bool: 'bool',
    dict: 'dict',
    str: 'str',
    list: 'list'
    }


def dataset_row_to_dict(row):
    """Semi-hacky helper function for extracting JSON for a single time series
    of a featureset. For now assumes single-channel data since that's what the
    front end can display.
    """
    out = {}
    if 'channel' in row:
        row = row.drop('channel')
    out['target'] = row.target.values.item() if 'target' in row else None
    if 'prediction' in row:
        if 'class_label' in row:  # {class label: probability}
            out['prediction'] = {six.u(label): value for label, value
                                 in zip(row.class_label.values,
                                        row.prediction.values)}
        else: # just a single predicted label or target
            out['prediction'] = row.prediction.values.item()
    else:
        out['prediction'] = None
    out['features'] = {f: row[f].item()
                       for f in row.data_vars if f != 'prediction'}

    return out


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        elif isinstance(o, bytes):
            return o.decode('utf-8')

        elif isinstance(o, peewee.Model):
            return o.__dict__()

        elif isinstance(o, peewee.SelectQuery):
            return [self.default(item) for item in list(o)]

        elif o is int:
            return 'int'

        elif o is float:
            return 'float'

        elif isinstance(o, np.ndarray):
            return o.tolist()

        elif isinstance(o, xr.Dataset):
            return {ts_name: dataset_row_to_dict(o.sel(name=ts_name))
                    for ts_name in o.name.values}

        elif type(o) is type and o in data_types:
            return data_types[o]

        return json.JSONEncoder.default(self, o)


def to_json(obj):
    return json.dumps(obj, cls=Encoder, indent=2)
