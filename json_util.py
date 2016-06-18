from datetime import datetime
import json
import peewee


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        elif isinstance(o, peewee.Model):
            return o.__dict__()

        return json.JSONEncoder.default(self, o)


def to_json(obj):
    return json.dumps(obj, cls=Encoder)
