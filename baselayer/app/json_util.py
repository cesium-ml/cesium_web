from datetime import datetime
import simplejson as json
import numpy as np
import pandas as pd
import peewee
import six


data_types = {
    int: 'int',
    float: 'float',
    bool: 'bool',
    dict: 'dict',
    str: 'str',
    list: 'list'
    }


class Encoder(json.JSONEncoder):
    """Extends json.JSONEncoder with additional capabilities/configurations."""
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

        elif isinstance(o, pd.DataFrame):
            o.columns = o.columns.droplevel('channel')  # flatten MultiIndex
            return o.to_dict(orient='index')

        elif type(o) is type and o in data_types:
            return data_types[o]

        return json.JSONEncoder.default(self, o)


def to_json(obj):
    return json.dumps(obj, cls=Encoder, indent=2, ignore_nan=True)
