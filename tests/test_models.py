import pytest
from selenium import webdriver
import uuid
import time
import os
from os.path import join as pjoin
import util

test_model_name = str(uuid.uuid4())


@pytest.fixture(scope="module")
def driver(request):
    from selenium import webdriver

    driver = webdriver.PhantomJS()
    request.addfinalizer(lambda: driver.close())

    return driver


def test_add_model(driver):
    driver.get('http://localhost:5000')
    driver.set_window_size(1920,1080)
    util.create_new_project(driver)
    util.add_dataset(driver)
    util.add_featureset(driver)

    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_partial_link_text('Create New Model').click()

    model_name = driver.find_element_by_css_selector('[name=modelName]')
    model_name.send_keys(test_model_name)

    driver.save_screenshot("/tmp/models_before_click.png")
    driver.find_element_by_class_name('btn-primary').click()

    driver.save_screenshot("/tmp/models_after_click.png")
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Model training begun')]")
    driver.save_screenshot("/tmp/models_after_click2.png")

    try:
        driver.implicitly_wait(2)
        status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
    except:
        driver.save_screenshot("/tmp/models_fail.png")
        raise

def test_delete_model(driver):
    driver.find_element_by_partial_link_text('Delete').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Model successfully deleted')]")

    util.delete_dataset(driver)
    util.delete_featureset(driver)
    util.delete_current_project(driver)
