import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import uuid
import os
import time
from os.path import join as pjoin
import util

test_featureset_name = str(uuid.uuid4())


@pytest.fixture(scope="module")
def driver(request):
    from selenium import webdriver

    driver = webdriver.PhantomJS()
    request.addfinalizer(lambda: driver.close())

    return driver


def test_add_new_featureset(driver):
    driver.get('http://localhost:5000')
    driver.set_window_size(1920,1080)
    util.create_new_project(driver)
    util.add_dataset(driver)

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()

    featureset_name = driver.find_element_by_css_selector('[name=featuresetName]')
    featureset_name.send_keys(test_featureset_name)

    # Test check/uncheck all features in group
    # amplitude = driver.find_element_by_css_selector('[name=sci_amplitude]')
    # assert amplitude.get_attribute('value') == 'true'
    # driver.save_screenshot("/tmp/1.png")
    # driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    # time.sleep(0.3)
    # driver.save_screenshot("/tmp/2.png")
    # assert amplitude.get_attribute('value') == 'false'
    # driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    # time.sleep(0.1)
    # assert amplitude.get_attribute('value') == 'true'

    # driver.find_element_by_id('react-tabs-14').click()
    # n_epochs = driver.find_element_by_css_selector('[name=obs_n_epochs]')
    # assert n_epochs.get_attribute('value') == 'true'
    # driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    # time.sleep(0.1)
    # assert n_epochs.get_attribute('value') == 'false'

    # driver.find_element_by_id('react-tabs-16').click()
    # driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    # assert driver.find_element_by_css_selector('[name=lmb_fold2P_slope_10percentile]')\
    #              .get_attribute('value') == 'false'


    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature computation begun')]")
    status_td = driver.find_element_by_xpath("//td[contains(text(),'In progress')]")

    driver.implicitly_wait(10)
    status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")


def test_delete_featureset(driver):
    driver.find_element_by_partial_link_text('Delete').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature set successfully deleted')]")
    try:
        el = driver.find_element_by_xpath(
            "//td[contains(text(),'{}')]".format(test_featureset_name))
    except NoSuchElementException:
        pass
    else:
        driver.save_screenshot("/tmp/after_fset_delete.png")
        raise Exception("Featureset still present in table after delete.")

    util.delete_dataset(driver)
    util.delete_current_project(driver)
