import pytest
import os


@pytest.fixture(scope="module", autouse=True)
def driver(request):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.binary_location = '/usr/bin/chromium-browser'

    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.set_window_size(1920, 1080)

    def close():
        driver.close()

    request.addfinalizer(close)

    return driver
