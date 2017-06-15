from baselayer.app.handlers.base import BaseHandler
from cesium.features.graphs import (feature_categories, feature_tags,
                                    dask_feature_graph, extra_feature_docs)


class FeatureListHandler(BaseHandler):
    def get(self):

        def get_docstring(func):
            return ' '.join([e.strip() for e in
                             func.__doc__.split('\n\n')[0].strip().split('\n')])

        feature_descriptions = {f: extra_feature_docs[f] if f in
                                extra_feature_docs else
                                get_docstring(dask_feature_graph[f][0]) for f in
                                dask_feature_graph if not f.startswith('_')}

        self.success({
            'features_by_category': feature_categories,
            'tags': feature_tags,
            'descriptions': feature_descriptions
        })
