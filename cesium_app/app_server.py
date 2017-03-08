import tornado.web
from tornado.web import url

from .config import cfg

import sys

from social_tornado.handlers import (
    AuthHandler, CompleteHandler, DisconnectHandler
    )

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
    PredictRawDataHandler
    )


def make_app():
    """Create and return a `tornado.web.Application` object with specified
    handlers and settings.
    """
    settings = {
        'template_path': './static',
        'autoreload': '--debug' in sys.argv,
        'cookie_secret': cfg['app']['secret-key'],

        # Python Social Auth configuration
        'SOCIAL_AUTH_STORAGE': 'cesium_app.models.TornadoStorage',
        'SOCIAL_AUTH_STRATEGY': 'social_tornado.strategy.TornadoStrategy',
        'SOCIAL_AUTH_AUTHENTICATION_BACKENDS': (
            'social_core.backends.google.GoogleOAuth2',
        )
    }

    if settings['cookie_secret'] == 'abc01234':
        print('!' * 80)
        print('  Your server is insecure. Please update the secret string in the')
        print('  configuration file!')
        print('!' * 80)

    handlers = [
        # Social Auth routes
        url(r'/login/(?P<backend>[^/]+)/?', AuthHandler, name='begin'),
        url(r'/complete/(?P<backend>[^/]+)/', CompleteHandler, name='complete'),
        url(r'/disconnect/(?P<backend>[^/]+)/?',
                DisconnectHandler, name='disconnect'),
        url(r'/disconnect/(?P<backend>[^/]+)/(?P<association_id>\d+)/?',
                DisconnectHandler, name='disconect_individual'),

#        (r'/', MainPageHandler),
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

        (r'/()', tornado.web.StaticFileHandler,
             {'path': 'static/', 'default_filename': 'index.html'}),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'})
    ]

    return tornado.web.Application(handlers, **settings)
