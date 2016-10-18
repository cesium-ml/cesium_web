from .base import BaseHandler

from cesium.features import feature_categories, feature_tags


class FeatureListHandler(BaseHandler):
    def get(self):
        self.success({
            'features_by_category': feature_categories,
            'feature_tags': feature_tags})
