import pytest
import os


@pytest.fixture(scope="module", autouse=True)
def driver(request):
    from selenium import webdriver

    # Phantom JS
    driver = webdriver.PhantomJS()

    # # Firefox marionette
    # from pyvirtualdisplay import Display
    # display = Display(visible=0, size=(1920, 1080))
    # from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    # caps = DesiredCapabilities.FIREFOX.copy()
    # caps["marionette"] = True
    # caps["binary"] = "/usr/bin/firefox"
    # driver = webdriver.Firefox(capabilities=caps)

    # Chrome
    # driver = webdriver.Chrome()

    driver.set_window_size(1920, 1080)

    def close():
        driver.close()
        # display.close()

    request.addfinalizer(close)

    return driver
