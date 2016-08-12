import pytest
import os


@pytest.fixture(scope="module", autouse=True)
def driver(request):
    from selenium import webdriver

    # driver = webdriver.PhantomJS()
    driver = webdriver.Chrome()

    driver.set_window_size(1920, 1080)

    def close():
        driver.close()

    request.addfinalizer(close)

    return driver
