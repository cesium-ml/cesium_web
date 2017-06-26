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
from cesium_app import models
from cesium_app.tests.fixtures import (TMP_DIR, ProjectFactory, DatasetFactory,
                                       FeaturesetFactory, ModelFactory,
                                       PredictionFactory)

print('Loading test configuration from _test_config.yaml')
basedir = pathlib.Path(os.path.dirname(__file__))
cfg = Config([(basedir/'../../config.yaml.example').absolute(),
              (basedir/'../../_test_config.yaml').absolute()])


def init_db():
    print('Setting test database to:', cfg['database'])
    models.db.init(**cfg['database'])

    return cfg


cfg = Config([(basedir/'../../config.yaml.example').absolute(),
              (basedir/'../../_test_config.yaml').absolute()])
models.init_db(**cfg['database'])


class MyCustomWebDriver(RequestMixin, webdriver.Chrome):
    def get(self, uri):
        return webdriver.Chrome.get(self, cfg['server:url'] + uri)

    def wait_for_xpath(self, xpath, timeout=1):
        return WebDriverWait(self, timeout).until(
            expected_conditions.presence_of_element_located((By.XPATH, xpath)))


@pytest.fixture(scope='module', autouse=True)
def driver(request):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()

    chromium = distutils.spawn.find_executable('chromium-browser')

    if chromium:
        chrome_options.binary_location = chromium

    chrome_options.add_argument('--browser.download.folderList=2')
    chrome_options.add_argument(
        '--browser.helperApps.neverAsk.saveToDisk=application/octet-stream')
    prefs = {'download.default_directory': '/tmp'}
    chrome_options.add_experimental_option('prefs', prefs)

    driver = MyCustomWebDriver(chrome_options=chrome_options)
    driver.set_window_size(1920, 1080)

    def close():
        driver.close()

    request.addfinalizer(close)

    # Authenticate by clicking login button
    driver.get('/')
    try:
        driver.wait_for_xpath('//div[contains(text(), "testuser@gmail.com")]')
    except TimeoutException:
        # Already logged in
        element = WebDriverWait(driver, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//a[@href="login/google-oauth2"]')))
        element.click()

    return driver


@pytest.fixture(scope='function', autouse=True)
def reset_state(request):
    def teardown():
        models.DBSession().rollback()
    request.addfinalizer(teardown)


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
