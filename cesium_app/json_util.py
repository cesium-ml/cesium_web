from datetime import datetime
import json
import peewee


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return o.decode('utf-8')

        elif isinstance(o, peewee.Model):
            return o.__dict__()

        elif isinstance(o, peewee.SelectQuery):
            return [self.default(item) for item in list(o)]

        return json.JSONEncoder.default(self, o)


def to_json(obj):
    return json.dumps(obj, cls=Encoder)
