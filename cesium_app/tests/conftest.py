'''Test fixture configuration.'''

import pytest
import os
import distutils.spawn
import types
from cesium_app import models as m
from cesium_app.config import cfg


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
    prefs = {'download.default_directory' : '/tmp'}
    chrome_options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.set_window_size(1920, 1080)

    def close():
        driver.close()

    request.addfinalizer(close)

    driver._get = driver.get
    def get(self, uri):
        return self._get(cfg['server']['url'] + uri)

    driver.set_window_size(1920, 1080)
    driver.get = types.MethodType(get, driver)

    return driver


@pytest.fixture(scope='session', autouse=True)
def remove_test_files(request):
    def teardown():
        for f in m.File.select():
            try:
                os.remove(f.file.uri)
            except:
                pass
    request.addfinalizer(teardown)
