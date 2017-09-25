'''Test fixture configuration.'''

import pytest
import os
import pathlib
import distutils.spawn
import types
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from seleniumrequests.request import RequestMixin
from pytest_factoryboy import register, LazyFixture
from baselayer.app.config import Config
from baselayer.app.test_util import (driver, MyCustomWebDriver, reset_state,
                                     set_server_url)
from cesium_app import models
from cesium_app.tests.fixtures import (TMP_DIR, ProjectFactory, DatasetFactory,
                                       FeaturesetFactory, ModelFactory,
                                       PredictionFactory)


print('Loading test configuration from _test_config.yaml')
basedir = pathlib.Path(os.path.dirname(__file__))/'../..'
cfg = Config([basedir/'config.yaml.example', basedir/'_test_config.yaml'])
set_server_url(cfg['server:url'])
print('Setting test database to:', cfg['database'])
models.init_db(**cfg['database'])


@pytest.fixture(scope='session', autouse=True)
def delete_temporary_files(request):
    def teardown():
        shutil.rmtree(TMP_DIR, ignore_errors=True)
    request.addfinalizer(teardown)


register(ProjectFactory)
register(DatasetFactory)
register(DatasetFactory, "unlabeled_dataset", name="unlabeled")
register(FeaturesetFactory)
register(ModelFactory)
register(PredictionFactory)
register(PredictionFactory, "unlabeled_prediction",
         dataset=LazyFixture("unlabeled_dataset"))
