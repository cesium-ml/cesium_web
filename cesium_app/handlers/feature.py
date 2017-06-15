import tornado.ioloop
import tornado.web

from cesium import featurize, time_series
from cesium.features import dask_feature_graph

from baselayer.app.handlers.base import BaseHandler, AccessError
from ..models import Dataset, Featureset, Project, File

from os.path import join as pjoin
import uuid
import datetime


class FeatureHandler(BaseHandler):
    def _get_featureset(self, featureset_id):
        try:
            f = Featureset.get(Featureset.id == featureset_id)
        except Featureset.DoesNotExist:
            raise AccessError('No such feature set')

        if not f.is_owned_by(self.current_user):
            raise AccessError('No such feature set')

        return f

    @tornado.web.authenticated
    def get(self, featureset_id=None):
        if featureset_id is not None:
            featureset_info = self._get_featureset(featureset_id)
        else:
            featureset_info = [f for p in Project.all(self.current_user)
                               for f in p.featuresets]

        self.success(featureset_info)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def _await_featurization(self, future, fset):
        """Note: we cannot use self.error / self.success here.  There is
        no longer an active, open request by the time this happens!
        That said, we can push notifications through to the frontend
        using flow.
        """
        try:
            result = yield future._result()

            fset.task_id = None
            fset.finished = datetime.datetime.now()
            fset.save()

            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={"note": "Calculation of featureset '{}' completed.".format(fset.name)})

        except Exception as e:
            fset.delete_instance()
            self.action('baselayer/SHOW_NOTIFICATION',
                        payload={"note": 'Cannot featurize {}: {}'.format(fset.name, e),
                                 "type": 'error'})
            print('Error featurizing:', type(e), e)

        self.action('cesium/FETCH_FEATURESETS')

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        data = self.get_json()
        featureset_name = data.get('featuresetName', '')
        dataset_id = int(data['datasetID'])
        features_to_use = [feature for (feature, selected) in data.items()
                           if feature in dask_feature_graph and selected]
        if not features_to_use:
            return self.error("At least one feature must be selected.")

        custom_feats_code = data['customFeatsCode'].strip()
        custom_script_path = None

        dataset = Dataset.get(Dataset.id == dataset_id)
        if not dataset.is_owned_by(self.current_user):
            raise AccessError('No such data set')

        fset_path = pjoin(self.cfg['paths:features_folder'],
                          '{}_featureset.npz'.format(uuid.uuid4()))

        fset = Featureset.create(name=featureset_name,
                                 file=File.create(uri=fset_path),
                                 project=dataset.project,
                                 features_list=features_to_use,
                                 custom_features_script=None)

        executor = yield self._get_executor()

        all_time_series = executor.map(time_series.load, dataset.uris)
        all_labels = executor.map(lambda ts: ts.label, all_time_series)
        all_features = executor.map(featurize.featurize_single_ts,
                                    all_time_series,
                                    features_to_use=features_to_use,
                                    custom_script_path=custom_script_path)
        computed_fset = executor.submit(featurize.assemble_featureset,
                                        all_features, all_time_series)
        imputed_fset = executor.submit(featurize.impute_featureset,
                                       computed_fset, inplace=False)
        future = executor.submit(featurize.save_featureset, imputed_fset,
                                 fset_path, labels=all_labels)
        fset.task_id = future.key
        fset.save()

        loop = tornado.ioloop.IOLoop.current()
        loop.spawn_callback(self._await_featurization, future, fset)

        self.success(fset, 'cesium/FETCH_FEATURESETS')

    @tornado.web.authenticated
    def delete(self, featureset_id):
        f = self._get_featureset(featureset_id)
        f.delete_instance()

        self.success(action='cesium/FETCH_FEATURESETS')

    @tornado.web.authenticated
    def put(self, featureset_id):
        f = self._get_featureset(featureset_id)
        self.error("Functionality for this endpoint is not yet implemented.")
