#!/usr/bin/env python

from cesium_app import app_server, model_util

app = app_server.make_app()
model_util.clear_tables()
