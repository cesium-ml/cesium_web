from baselayer.app.handlers.base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from baselayer.app.access import auth_or_token
from ..models import DBSession, Project, Dataset, DatasetFile
from .. import util

from cesium import data_management, time_series
from cesium.util import shorten_fname

import os
from os.path import join as pjoin
import uuid
import base64
import tarfile


class DatasetHandler(BaseHandler):
    @auth_or_token
    def post(self):
        data = self.get_json()
        if not 'tarFile' in data:
            return self.error('No tar file uploaded')

        zipfile = data['tarFile']
        tarball_content_types = ('data:application/gzip;base64',
                                 'data:application/x-gzip;base64')

        if not zipfile['body'].startswith(tarball_content_types):
            return self.error('Invalid tar file - please ensure file is gzip '
                              'format.')

        if zipfile['name'] == '':
            return self.error('Empty tar file uploaded')

        dataset_name = data['datasetName']
        project_id = data['projectID']

        zipfile_name = (str(uuid.uuid4()) + "_" +
                        util.secure_filename(zipfile['name']))
        zipfile_path = pjoin(self.cfg['paths:upload_folder'], zipfile_name)

        for prefix in tarball_content_types:
            zipfile['body'] = zipfile['body'].replace(prefix, '')
        with open(zipfile_path, 'wb') as f:
            f.write(base64.b64decode(zipfile['body']))
        try:
            tarfile.open(zipfile_path)
        except tarfile.ReadError:
            os.remove(zipfile_path)
            return self.error('Invalid tar file - please ensure file is gzip '
                              'format.')

        # Header file is optional for unlabled data w/o metafeatures
        if 'headerFile' in data:
            headerfile = data['headerFile']
            headerfile_name = (str(uuid.uuid4()) + "_" +
                               util.secure_filename(headerfile['name']))
            headerfile_path = pjoin(self.cfg['paths:upload_folder'], headerfile_name)

            with open(headerfile_path, 'w') as f:
                f.write(headerfile['body'])

        else:
            headerfile_path = None

        p = Project.query.filter(Project.id == project_id).one()
        ts_paths = data_management.parse_and_store_ts_data(
            zipfile_path,
            self.cfg['paths:ts_data_folder'],
            headerfile_path)
        meta_features = list(time_series.load(ts_paths[0]).meta_features.keys())
        unique_ts_paths = [os.path.join(os.path.dirname(ts_path),
                                        str(uuid.uuid4()) + "_" +
                                        util.secure_filename(ts_path))
                           for ts_path in ts_paths]
        d = Dataset(name=dataset_name, project=p, meta_features=meta_features)
        for old_path, new_path in zip(ts_paths, unique_ts_paths):
            os.rename(old_path, new_path)
            d.files.append(DatasetFile(name=shorten_fname(old_path),
                                       uri=new_path))
        DBSession().add(d)
        DBSession().commit()

        return self.success(d.display_info(), 'cesium/FETCH_DATASETS')

    @auth_or_token
    def get(self, dataset_id=None):
        if dataset_id is not None:
            dataset = Dataset.get_if_owned_by(dataset_id, self.current_user)
            dataset_info = dataset.display_info()
        else:
            datasets = [d for p in self.current_user.projects
                        for d in p.datasets]
            dataset_info = [d.display_info() for d in datasets]

        return self.success(dataset_info)

    @auth_or_token
    def delete(self, dataset_id):
        d = Dataset.get_if_owned_by(dataset_id, self.current_user)
        DBSession().delete(d)
        DBSession().commit()
        return self.success(action='cesium/FETCH_DATASETS')
