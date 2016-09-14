from .base import BaseHandler, AccessError
from ..models import Project, Dataset
from .. import util
from ..config import cfg

from cesium import data_management

from os.path import join as pjoin
import uuid


class DatasetHandler(BaseHandler):
    def _get_dataset(self, dataset_id):
        try:
            d = Dataset.get(Dataset.id == dataset_id)
        except Dataset.DoesNotExist:
            raise AccessError('No such dataset')

        if not d.is_owned_by(self.get_username()):
            raise AccessError('No such dataset')

        return d

    def post(self):
        if not 'tarFile' in self.request.files:
            return self.error('No tar file uploaded')

        zipfile = self.request.files['tarFile'][0]

        if zipfile.filename == '':
            return self.error('Empty tar file uploaded')

        dataset_name = self.get_argument('datasetName')
        project_id = self.get_argument('projectID')

        zipfile_name = (str(uuid.uuid4()) + "_" +
                        str(util.secure_filename(zipfile.filename)))
        zipfile_path = pjoin(cfg['paths']['upload_folder'], zipfile_name)

        with open(zipfile_path, 'wb') as f:
            f.write(zipfile['body'])

        # Header file is optional for unlabled data w/o metafeatures
        if 'headerFile' in self.request.files:
            headerfile = self.request.files['headerFile'][0]
            headerfile_name = (str(uuid.uuid4()) + "_" +
                               str(util.secure_filename(headerfile.filename)))
            headerfile_path = pjoin(cfg['paths']['upload_folder'], headerfile_name)

            with open(headerfile_path, 'wb') as f:
                f.write(headerfile['body'])

        else:
            headerfile_path = None

        p = Project.get(Project.id == project_id)
        # TODO this should give unique names to the time series files
        time_series = data_management.parse_and_store_ts_data(
            zipfile_path,
            cfg['paths']['ts_data_folder'],
            headerfile_path)
        ts_paths = [ts.path for ts in time_series]
        d = Dataset.add(name=dataset_name, project=p, file_uris=ts_paths)

        return self.success(d, 'cesium/FETCH_DATASETS')

    def get(self, dataset_id=None):
        if dataset_id is not None:
            datasets = self._get_dataset(dataset_id)
        else:
            datasets = [d for p in Project.all(self.get_username())
                            for d in p.datasets]

        return self.success(datasets)

    def delete(self, dataset_id):
        d = self._get_dataset(dataset_id)
        d.delete_instance()
        return self.success(action='cesium/FETCH_DATASETS')
