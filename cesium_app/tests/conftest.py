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
from pytest_factoryboy import register
from baselayer.app.config import Config
from baselayer.app.test_util import (driver, load_test_config,
                                     MyCustomWebDriver, reset_state)
from cesium_app import models
from cesium_app.tests.fixtures import (TMP_DIR, ProjectFactory, DatasetFactory,
                                       FeaturesetFactory, ModelFactory,
                                       PredictionFactory)


basedir = pathlib.Path(os.path.dirname(__file__))
cfg = load_test_config([(basedir/'../../_test_config.yaml').absolute()])


@pytest.fixture(scope='session', autouse=True)
def delete_temporary_files(request):
    def teardown():
        shutil.rmtree(TMP_DIR, ignore_errors=True)
    request.addfinalizer(teardown)


register(ProjectFactory)
register(DatasetFactory)
register(DatasetFactory, "unlabeled_dataset")
register(FeaturesetFactory)
register(ModelFactory)
register(PredictionFactory)
register(PredictionFactory, "unlabeled_prediction")


@pytest.fixture
def unlabeled_dataset__name():
    """Set `.name` property of fixture `unlabeled_dataset`."""
    return "unlabeled"


@pytest.fixture
def unlabeled_prediction__dataset(unlabeled_dataset):
    """Set `.dataset` property of fixture `unlabeled_prediction`."""
    return unlabeled_dataset
