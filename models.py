import datetime
import peewee as pw
from playhouse.fields import ManyToManyField

from config import cfg
 

db = pw.PostgresqlDatabase(**cfg['database'], autocommit=True,
                           autorollback=True)

class BaseModel(pw.Model):
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


TimeSeriesDataset = Dataset.time_series.get_through_model()


def create_tables():
    db.create_tables([Project, TimeSeries, Dataset, TimeSeriesDataset],
                     safe=True)
