from .base import BaseHandler

from cesium.features import CADENCE_FEATS, GENERAL_FEATS, LOMB_SCARGLE_FEATS


class FeatureListHandler(BaseHandler):
    def get(self):
        self.success({
            "obs_features": CADENCE_FEATS,
            "sci_features": GENERAL_FEATS,
            "lmb_features": LOMB_SCARGLE_FEATS})
