import tornado.web

import os
import sys
import pathlib

from .config import Config
from . import models

# This provides `login`, `complete`, and `disconnect` endpoints
from social_tornado.routes import SOCIAL_AUTH_ROUTES

from .handlers import (
    MainPageHandler,
    ProjectHandler,
    DatasetHandler,
    FeatureHandler,
    ModelHandler,
    PredictionHandler,
    FeatureListHandler,
    SklearnModelsHandler,
    SocketAuthTokenHandler,
    PlotFeaturesHandler,
    PredictRawDataHandler,
    ProfileHandler,
    LogoutHandler
)


def load_config(config_files=None):
    if config_files is None:
        basedir = pathlib.Path(os.path.dirname(__file__))/'..'
        config_files = (basedir/'cesium.yaml.example', basedir/'cesium.yaml')
        config_files = (c.absolute() for c in config_files)

    cfg = Config(config_files)

    return cfg


def make_app(config_files=None):
    """Create and return a `tornado.web.Application` object with specified
    handlers and settings.

    Parameters
    ----------
    config_files : list of str
        Filenames of configuration files, loaded in the order specified.
        By default, 'cesium.yaml.example' is used for defaults and 'cesium.yaml'
        for further customizations.

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

    # Tornado settings
    settings = {
        'template_path': './static',
        'autoreload': '--debug' in sys.argv,
        'cookie_secret': cfg['app:secret-key'],
        'login_url': '/',

        # Python Social Auth configuration
        'SOCIAL_AUTH_USER_MODEL': 'cesium_app.models.User',
        'SOCIAL_AUTH_STORAGE': 'cesium_app.psa.TornadoPeeweeStorage',
        'SOCIAL_AUTH_STRATEGY': 'social_tornado.strategy.TornadoStrategy',
        'SOCIAL_AUTH_AUTHENTICATION_BACKENDS': (
            'social_core.backends.google.GoogleOAuth2',
        ),
        'SOCIAL_AUTH_LOGIN_URL': '/',
        'SOCIAL_AUTH_LOGIN_REDIRECT_URL': '/',  # on success
        'SOCIAL_AUTH_LOGIN_ERROR_URL': '/login-error/',

        'SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL': True,
        'SOCIAL_AUTH_SESSION_EXPIRATION': True,

        'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY':
            cfg['server:auth:google_oauth2_key'],
        'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET': \
            cfg['server:auth:google_oauth2_secret'],
    }

    handlers = SOCIAL_AUTH_ROUTES + [
        (r'/project(/.*)?', ProjectHandler),
        (r'/dataset(/.*)?', DatasetHandler),
        (r'/features(/.*)?', FeatureHandler),
        (r'/models(/.*)?', ModelHandler),
        (r'/predictions(/[0-9]+)?', PredictionHandler),
        (r'/predictions/([0-9]+)/(download)', PredictionHandler),
        (r'/predict_raw_data', PredictRawDataHandler),
        (r'/features_list', FeatureListHandler),
        (r'/socket_auth_token', SocketAuthTokenHandler),
        (r'/sklearn_models', SklearnModelsHandler),
        (r'/plot_features/(.*)', PlotFeaturesHandler),
        (r'/profile', ProfileHandler),
        (r'/logout', LogoutHandler),

        (r'/()', MainPageHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r'/(favicon.png)', tornado.web.StaticFileHandler, {'path': 'static/'})
    ]

    if cfg['server:auth:debug_login']:
        settings['SOCIAL_AUTH_AUTHENTICATION_BACKENDS'] = (
            'cesium_app.psa.FakeGoogleOAuth2',
        )

    app = tornado.web.Application(handlers, **settings)
    models.db.init(**cfg['database'])
    app.cfg = cfg

    return app
