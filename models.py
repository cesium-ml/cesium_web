import datetime
import inspect
import sys

import peewee as pw
from playhouse.fields import ManyToManyField
from playhouse.shortcuts import model_to_dict
from json_util import to_json

from config import cfg


db = pw.PostgresqlDatabase(**cfg['database'], autocommit=True,
                           autorollback=True)

class BaseModel(pw.Model):
    def __str__(self):
        return to_json(model_to_dict(self, recurse=False, backrefs=False))

    class Meta:
        database = db


class Project(BaseModel):
    """
    ORM model of the Project table
    """
    name = pw.CharField()
    description = pw.CharField(null=True)
    created = pw.DateTimeField(default=datetime.datetime.now)


class TimeSeries(BaseModel):
    """
    ORM model of the TimeSeries table
    """
    filename = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)


class Dataset(BaseModel):
    """
    ORM model of the Dataset table
    """
    project = pw.ForeignKeyField(Project, on_delete='CASCADE')
    name = pw.CharField()
    created = pw.DateTimeField(default=datetime.datetime.now)
    time_series = ManyToManyField(TimeSeries)


class UserProject(BaseModel):
    user = pw.CharField()
    project = pw.ForeignKeyField(Project, related_name='users',
                                 on_delete='CASCADE')

    class Meta:
        indexes = (
            (('user', 'project'), True),
        )


TimeSeriesDataset = Dataset.time_series.get_through_model()

models = [
    obj for (name, obj) in inspect.getmembers(sys.modules[__name__])
    if inspect.isclass(obj) and issubclass(obj, BaseModel)
    and not obj == BaseModel
]


def create_tables():
    db.create_tables(models, safe=True)


def drop_tables():
    db.drop_tables(models, safe=True, cascade=True)


if __name__ == "__main__":
    print("Dropping all tables...")
    drop_tables()
    print("Creating tables: {}".format([m.__name__ for m in models]))
    create_tables()

    print("Inserting dummy projects...")
    for i in range(5):
        p = Project(name='test project {}'.format(i))
        p.save()

        print(p)

    print("Creating dummy project owners...")
    p = Project.get()
    UserProject(user='testuser@gmail.com', project=p).save()
