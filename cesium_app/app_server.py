import tornado.web
from tornado.web import url

from .config import cfg

import sys

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
    ProfileHandler
    )


def make_app():
    """Create and return a `tornado.web.Application` object with specified
    handlers and settings.
    """
    settings = {
        'template_path': './static',
        'autoreload': '--debug' in sys.argv,
        'cookie_secret': cfg['app']['secret-key'],
        'login_url': '/',

        # Python Social Auth configuration
        'SOCIAL_AUTH_USER_MODEL': 'cesium_app.models.User',
        'SOCIAL_AUTH_STORAGE': 'cesium_app.models.TornadoStorage',
        'SOCIAL_AUTH_STRATEGY': 'social_tornado.strategy.TornadoStrategy',
        'SOCIAL_AUTH_AUTHENTICATION_BACKENDS': (
            'social_core.backends.google.GoogleOAuth2',
        ),
        'SOCIAL_AUTH_LOGIN_URL': '/',
        'SOCIAL_AUTH_LOGIN_REDIRECT_URL': '/',  # on success
        'SOCIAL_AUTH_LOGIN_ERROR_URL': '/login-error/',

        'SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL': True,

        # From https://console.developers.google.com/
        # - Create Client ID
        # - Javascript origins: https://localhost:5000
        # - Authorized redirect URLs: http://localhost:5000/complete/google-oauth2/
        #
        # You need to have Google+ API enabled; it takes a few minutes to activate.

        'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY': '544669011322-76ebnoj0fhvle168682rvmivc3fpchpi.apps.googleusercontent.com',
        'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET': 'b22Ya_1xljAqmM9gVh7KsppO',
    }

    if settings['cookie_secret'] == 'abc01234':
        print('!' * 80)
        print('  Your server is insecure. Please update the secret string in the')
        print('  configuration file!')
        print('!' * 80)

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

        (r'/()', MainPageHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'})
    ]

    return tornado.web.Application(handlers, **settings)
