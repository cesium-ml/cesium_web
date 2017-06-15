import tornado.web

import os
import sys
import pathlib

from baselayer.app.config import Config
from . import models
from baselayer.app import model_util
from baselayer.app.app_server import (handlers as baselayer_handlers,
                                      settings as baselayer_settings)
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


def make_app(config_files=None, debug=False):
    """Create and return a `tornado.web.Application` object with specified
    handlers and settings.

    Parameters
    ----------
    config_files : list of str
        Filenames of configuration files, loaded in the order specified.
        By default, 'config.yaml.example' is used for defaults and 'config.yaml'
        for further customizations.
    debug : bool
        Whether or not to start the app in debug mode.  In debug mode,
        changed source files are immediately reloaded.

    """
    # Cesium settings
    cfg = load_config(config_files)

    if cfg['cookie_secret'] == 'abc01234':
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
    settings.update({'autoreload': debug})  # Specify additional settings here

    app = tornado.web.Application(handlers, **settings)
    models.db.init(**cfg['database'])
    model_util.create_tables()
    model_util.create_tables(models.app_models)
    app.cfg = cfg

    return app
