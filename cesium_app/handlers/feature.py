import tornado.ioloop

from cesium import featurize, time_series
from cesium.features import dask_feature_graph

from baselayer.app.handlers.base import BaseHandler
from baselayer.app.custom_exceptions import AccessError
from baselayer.app.access import auth_or_token
from ..models import DBSession, Dataset, Featureset, Project

from .progressbar import WebSocketProgressBar

from os.path import join as pjoin
import uuid
import datetime
from io import StringIO
import pandas as pd


class FeatureHandler(BaseHandler):
    @auth_or_token
    def get(self, featureset_id=None, action=None):
        if action == 'download':
            featureset = Featureset.get_if_owned_by(featureset_id,
                                                    self.current_user)
            fset_path = featureset.file_uri
            fset, data = featurize.load_featureset(fset_path)
            if 'labels' in data:
                fset['labels'] = data['labels']
            self.set_header("Content-Type", 'text/csv; charset="utf-8"')
            self.set_header(
                "Content-Disposition", "attachment; "
                f"filename=cesium_featureset_{featureset.project.name}"
                f"_{featureset.name}_{featureset.finished}.csv")
            self.write(fset.to_csv(index=True))
        else:
            if featureset_id is not None:
                featureset_info = Featureset.get_if_owned_by(featureset_id,
                                                             self.current_user)
            else:
                featureset_info = [f for p in self.current_user.projects
                                   for f in p.featuresets]
                featureset_info.sort(key=lambda f: f.created_at, reverse=True)

            self.success(featureset_info)

    @auth_or_token
    async def _await_featurization(self, future, fset):
        """Note: we cannot use self.error / self.success here.  There is
        no longer an active, open request by the time this happens!
        That said, we can push notifications through to the frontend
        using flow.
        """
        def progressbar_update(payload):
            payload.update({'fsetID': fset.id})
            self.action('cesium/FEATURIZE_PROGRESS', payload=payload)

        try:
            WebSocketProgressBar([future], progressbar_update, interval=2)
            result = await future

            fset = DBSession().merge(fset)
            fset.task_id = None
            fset.finished = datetime.datetime.now()
            DBSession().commit()

            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={"note": "Calculation of featureset '{}' completed.".format(fset.name)})

        except Exception as e:
            DBSession().delete(fset)
            DBSession().commit()
            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={"note": 'Cannot featurize {}: {}'.format(fset.name, e),
                                 "type": 'error'})
            print('Error featurizing:', type(e), e)

        self.action('cesium/FETCH_FEATURESETS')

    @auth_or_token
    async def post(self):
        data = self.get_json()
        featureset_name = data.get('featuresetName', '')
        dataset_id = int(data['datasetID'])
        features_to_use = [feature for (feature, selected) in data.items()
                           if feature in dask_feature_graph and selected]
        if not features_to_use:
            return self.error("At least one feature must be selected.")

        custom_feats_code = data['customFeatsCode'].strip()
        custom_script_path = None

        dataset = Dataset.query.filter(Dataset.id == dataset_id).one()
        if not dataset.is_owned_by(self.current_user):
            raise AccessError('No such data set')

        fset_path = pjoin(self.cfg['paths:features_folder'],
                          '{}_featureset.npz'.format(uuid.uuid4()))

        fset = Featureset(name=featureset_name,
                          file_uri=fset_path,
                          project=dataset.project,
                          dataset=dataset,
                          features_list=features_to_use,
                          custom_features_script=None)
        DBSession().add(fset)

        client = await self._get_client()

        all_time_series = client.map(time_series.load,
                                     [f.uri for f in dataset.files])
        all_labels = client.map(lambda ts: ts.label, all_time_series)
        all_features = client.map(featurize.featurize_single_ts,
                                  all_time_series,
                                  features_to_use=features_to_use,
                                  custom_script_path=custom_script_path,
                                  raise_exceptions=False)
        computed_fset = client.submit(featurize.assemble_featureset,
                                      all_features, all_time_series)
        imputed_fset = client.submit(featurize.impute_featureset,
                                     computed_fset, inplace=False)
        future = client.submit(featurize.save_featureset, imputed_fset,
                               fset_path, labels=all_labels)
        fset.task_id = future.key
        DBSession().commit()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_featurization, future, fset)

        self.success(fset, 'cesium/FETCH_FEATURESETS')

    @auth_or_token
    def delete(self, featureset_id):
        f = Featureset.get_if_owned_by(featureset_id, self.current_user)
        DBSession().delete(f)
        DBSession().commit()
        self.success(action='cesium/FETCH_FEATURESETS')

    @auth_or_token
    def put(self, featureset_id):
        f = Featureset.get_if_owned_by(featureset_id, self.current_user)
        self.error("Functionality for this endpoint is not yet implemented.")


class PrecomputedFeaturesHandler(BaseHandler):
    @auth_or_token
    def post(self):
        data = self.get_json()
        if data['datasetID'] not in [None, 'None']:
            dataset = Dataset.query.filter(Dataset.id == data['datasetID']).one()
        else:
            dataset = None
        current_project = Project.get_if_owned_by(data['projectID'],
                                                  self.current_user)
        feature_data = StringIO(data['dataFile']['body'])
        fset = pd.read_csv(feature_data, index_col=0, header=[0, 1])
        if 'labels' in fset:
            labels = fset.pop('labels').values.ravel()
            if labels.dtype == 'O':
                labels = [str(label) for label in labels]
        else:
            labels = [None]
        fset_path = pjoin(
            self.cfg['paths:features_folder'],
            '{}_{}.npz'.format(uuid.uuid4(), data['dataFile']['name']))

        featurize.save_featureset(fset, fset_path, labels=labels)

        # Meta-features will have channel values of an empty string or a string
        # beginning with 'Unnamed:'
        features_list = [el[0] for el in fset.columns.tolist() if
                         (el[1] != '' and not el[1].startswith('Unnamed:'))]

        featureset = Featureset(name=data['featuresetName'],
                                file_uri=fset_path,
                                project=current_project,
                                dataset=dataset,
                                features_list=features_list,
                                finished=datetime.datetime.now(),
                                custom_features_script=None)
        DBSession().add(featureset)
        DBSession().commit()

        self.success(featureset, 'cesium/FETCH_FEATURESETS')
