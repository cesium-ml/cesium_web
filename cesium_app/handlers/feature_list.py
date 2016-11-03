from .base import BaseHandler
from cesium.features.graphs import (feature_categories, feature_tags,
                                    dask_feature_graph, extra_feature_docs)


class FeatureListHandler(BaseHandler):
    def get(self):
        feature_descriptions = {}
        for feature_name in [e for e in dask_feature_graph
                             if not e.startswith('_')]:
            description = (extra_feature_docs[feature_name] if
                           feature_name in extra_feature_docs else
                           ' '.join([e.strip() for e in
                                     dask_feature_graph[feature_name][0]
                                     .__doc__.split('\n\n')[0]
                                     .strip().split('\n')]))
            feature_descriptions[feature_name] = description

        self.success({
            'features_by_category': feature_categories,
            'tags': feature_tags,
            'descriptions': feature_descriptions
        })
