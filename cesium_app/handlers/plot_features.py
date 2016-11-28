from .base import BaseHandler
from .. import plot
from ..models import Featureset


class PlotFeaturesHandler(BaseHandler):
    def get(self, featureset_id):
        fset = Featureset.get_if_owned(featureset_id, self.get_username())
        features_to_plot = sorted(fset.features_list)[0:4]  # TODO from form
        js, div = plot.feature_scatterplot(fset.file.uri, features_to_plot)
        self.success({'js': js, 'div': div})
