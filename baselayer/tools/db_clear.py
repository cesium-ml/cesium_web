#!/usr/bin/env python

from cesium_app import app_server
from cesium_app import models
from baselayer.app import model_util

app = app_server.make_app()
model_util.clear_tables()
model_util.clear_tables(models.app_models)
