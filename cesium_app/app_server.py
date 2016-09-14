import tornado.web

import sys


from .handlers import (
    ProjectHandler,
    DatasetHandler,
    FeatureHandler,
    ModelHandler,
    PredictionHandler,
    FeatureListHandler,
    SklearnModelsHandler,
    SocketAuthTokenHandler,
    PlotFeaturesHandler
    )


def make_app():
    settings = {
        'static_path': '../public',
        'autoreload': '--debug' in sys.argv
        }

    handlers = [
        (r'/project(/.*)?', ProjectHandler),
        (r'/dataset(/.*)?', DatasetHandler),
        (r'/features(/.*)?', FeatureHandler),
        (r'/models(/.*)?', ModelHandler),
        (r'/predictions(/.*)?', PredictionHandler),
        (r'/features_list', FeatureListHandler),
        (r'/socket_auth_token', SocketAuthTokenHandler),
        (r'/sklearn_models', SklearnModelsHandler),
        (r'/plot_features/(.*)', PlotFeaturesHandler),
        (r'/(.*)', tornado.web.StaticFileHandler,
             {'path': 'public/', 'default_filename': 'index.html'})
    ]

    return tornado.web.Application(handlers, **settings)
