from .base import BaseHandler
from .. import plot
from ..models import Featureset

import tornado.web


class PlotFeaturesHandler(BaseHandler):
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
        fset = self._get_featureset(featureset_id)
        features_to_plot = sorted(fset.features_list)[0:4]
        data, layout = plot.feature_scatterplot(fset.file.uri, features_to_plot)

        self.success({'data': data, 'layout': layout})
