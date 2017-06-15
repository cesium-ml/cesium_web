import tornado.web

# This provides `login`, `complete`, and `disconnect` endpoints
from social_tornado.routes import SOCIAL_AUTH_ROUTES

from .handlers import (
    MainPageHandler,
    SocketAuthTokenHandler,
    ProfileHandler,
    LogoutHandler
)

from .config import load_config
cfg = load_config()


# Tornado settings
settings = {
    'template_path': './static',
#    'autoreload': debug,
    'cookie_secret': cfg['app:secret-key'],
    'login_url': '/',

    # Python Social Auth configuration
    'SOCIAL_AUTH_USER_MODEL': 'baselayer.app.models.User',
    'SOCIAL_AUTH_STORAGE': 'baselayer.app.psa.TornadoPeeweeStorage',
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
    (r'/socket_auth_token', SocketAuthTokenHandler),
    (r'/profile', ProfileHandler),
    (r'/logout', LogoutHandler),

    (r'/()', MainPageHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
    (r'/(favicon.png)', tornado.web.StaticFileHandler, {'path': 'static/'})
]
