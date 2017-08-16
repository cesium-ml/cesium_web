import tornado.web

import os
import sys
import pathlib

from baselayer.app.config import Config
from . import models
from baselayer.app import model_util
from baselayer.app.config import load_config

# This provides `login`, `complete`, and `disconnect` endpoints
from social_tornado.routes import SOCIAL_AUTH_ROUTES

from .handlers import (
    ProjectHandler,
    DatasetHandler,
    FeatureHandler,
    ModelHandler,
    PredictionHandler,
    FeatureListHandler,
    SklearnModelsHandler,
    PlotFeaturesHandler,
    PredictRawDataHandler
)


def make_app(cfg, baselayer_handlers, baselayer_settings):
    """Create and return a `tornado.web.Application` object with specified
    handlers and settings.

    Parameters
    ----------
    cfg : Config
        Loaded configuration.  Can be specified with '--config'
        (multiple uses allowed).
    baselayer_handlers : list
        Tornado handlers needed for baselayer to function.
    baselayer_settings : cfg
        Settings needed for baselayer to function.

    """
    if baselayer_settings['cookie_secret'] == 'abc01234':
        print('!' * 80)
        print('  Your server is insecure. Please update the secret string ')
        print('  in the configuration file!')
        print('!' * 80)

    for path_name, path in cfg['paths'].items():
        if not os.path.exists(path):
            print("Creating %s" % path)
            try:
                os.makedirs(path)
            except Exception as e:
                print(e)

    handlers = baselayer_handlers + [
        (r'/project(/.*)?', ProjectHandler),
        (r'/dataset(/.*)?', DatasetHandler),
        (r'/features(/.*)?', FeatureHandler),
        (r'/models(/.*)?', ModelHandler),
        (r'/predictions(/[0-9]+)?', PredictionHandler),
        (r'/predictions/([0-9]+)/(download)', PredictionHandler),
        (r'/predict_raw_data', PredictRawDataHandler),
        (r'/features_list', FeatureListHandler),
        (r'/sklearn_models', SklearnModelsHandler),
        (r'/plot_features/(.*)', PlotFeaturesHandler)
    ]

    settings = baselayer_settings
    # settings.update({})  # Specify additional settings here

    app = tornado.web.Application(handlers, **settings)
    models.init_db(**cfg['database'])
    model_util.create_tables()

    return app
