from datetime import datetime
import json
import peewee


data_types = {
    int: 'int',
    float: 'float',
    bool: 'bool',
    dict: 'dict',
    str: 'str',
    list: 'list'
    }


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

        elif o in data_types:
            return data_types[o]

        return json.JSONEncoder.default(self, o, indent=2)


def to_json(obj):
    return json.dumps(obj, cls=Encoder)
