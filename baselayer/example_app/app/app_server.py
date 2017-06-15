import tornado.web

import os
import sys
import pathlib

from baselayer.app import Config


def make_app(handlers, settings):
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
    # TODO: handle config files by parsing sys.argv
    #       handle debug flag

    # baselayer settings
#    cfg = load_config(config_files)

    ## if cfg['cookie_secret'] == 'abc01234':
    ##     print('!' * 80)
    ##     print('  Your server is insecure. Please update the secret string ')
    ##     print('  in the configuration file!')
    ##     print('!' * 80)

    ## for path_name, path in cfg['paths'].items():
    ##     if not os.path.exists(path):
    ##         print("Creating %s" % path)
    ##         try:
    ##             os.makedirs(path)
    ##         except Exception as e:
    ##             print(e)

    app = tornado.web.Application(handlers, **settings)
#    models.db.init(**cfg['database'])
#    model_util.create_tables()
#    model_util.create_tables(models.app_models)
#    app.cfg = cfg

    return app
