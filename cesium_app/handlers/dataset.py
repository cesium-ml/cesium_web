from .base import BaseHandler, AccessError
from ..models import Project, Dataset
from .. import util
from ..config import cfg

from cesium import data_management, time_series
from cesium.util import shorten_fname
from ..tests.fixtures import create_test_dataset

import os
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
        if self.get_argument('create_example'):
            project_id = self.get_argument('projectID')
            p = Project.get(Project.id == project_id)
            with create_test_dataset(p, delete_after=False) as d:
                return self.success(d, 'cesium/FETCH_DATASETS')

        if not 'tarFile' in self.request.files:
            return self.error('No tar file uploaded')

        zipfile = self.request.files['tarFile'][0]

        if zipfile.filename == '':
            return self.error('Empty tar file uploaded')

        dataset_name = self.get_argument('datasetName')
        project_id = self.get_argument('projectID')

        zipfile_name = (str(uuid.uuid4()) + "_" +
                        util.secure_filename(zipfile.filename))
        zipfile_path = pjoin(cfg['paths']['upload_folder'], zipfile_name)

        with open(zipfile_path, 'wb') as f:
            f.write(zipfile['body'])

        # Header file is optional for unlabled data w/o metafeatures
        if 'headerFile' in self.request.files:
            headerfile = self.request.files['headerFile'][0]
            headerfile_name = (str(uuid.uuid4()) + "_" +
                               util.secure_filename(headerfile.filename))
            headerfile_path = pjoin(cfg['paths']['upload_folder'], headerfile_name)

            with open(headerfile_path, 'wb') as f:
                f.write(headerfile['body'])

        else:
            headerfile_path = None

        p = Project.get(Project.id == project_id)
        # TODO this should give unique names to the time series files
        ts_paths = data_management.parse_and_store_ts_data(
            zipfile_path,
            cfg['paths']['ts_data_folder'],
            headerfile_path)
        meta_features = list(time_series.load(ts_paths[0]).meta_features.keys())
        unique_ts_paths = [os.path.join(os.path.dirname(ts_path),
                                        str(uuid.uuid4()) + "_" +
                                        util.secure_filename(ts_path))
                           for ts_path in ts_paths]
        for old_path, new_path in zip(ts_paths, unique_ts_paths):
            os.rename(old_path, new_path)
        file_names = [shorten_fname(ts_path) for ts_path in ts_paths]
        d = Dataset.add(name=dataset_name, project=p, file_names=file_names,
                        file_uris=unique_ts_paths, meta_features=meta_features)

        return self.success(d, 'cesium/FETCH_DATASETS')

    def get(self, dataset_id=None):
        if dataset_id is not None:
            dataset = self._get_dataset(dataset_id)
            dataset_info = dataset.display_info()
        else:
            datasets = [d for p in Project.all(self.get_username())
                            for d in p.datasets]
            dataset_info = [d.display_info() for d in datasets]

        return self.success(dataset_info)

    def delete(self, dataset_id):
        d = self._get_dataset(dataset_id)
        d.delete_instance()
        return self.success(action='cesium/FETCH_DATASETS')
