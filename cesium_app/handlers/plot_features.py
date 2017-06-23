from baselayer.app.handlers.base import BaseHandler
from .. import plot
from ..models import Featureset

import tornado.web


class PlotFeaturesHandler(BaseHandler):
    def post(self):
        print("Got a post request for plotting ")
        data = self.get_json()
        print(data)

        featureset_id = data['featuresetId']
        fset = Featureset.get_if_owned(featureset_id, self.current_user)

        if data['tags']:
            features_to_plot = data['tags'].split(',')
            docs_json, render_items = plot.feature_scatterplot(fset.file_uri, features_to_plot)
        else:
            docs_json, render_items = None, None

        return self.success({'featuresetId': featureset_id, 'docs_json': docs_json, 'render_items': render_items})
