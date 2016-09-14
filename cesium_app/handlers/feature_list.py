from .base import BaseHandler

from cesium import obs_feature_tools as oft
from cesium import science_feature_tools as sft


class FeatureListHandler(BaseHandler):
    def get(self):
        self.success({
            "obs_features": oft.FEATURES_LIST,
            "sci_features": [el for el in sft.FEATURES_LIST if el not in
                                sft.LOMB_SCARGLE_FEATURES_LIST],
            "lmb_features": sft.LOMB_SCARGLE_FEATURES_LIST})
