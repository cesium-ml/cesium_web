import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin
from util import test_project, test_dataset, test_featureset, test_model

test_model_name = str(uuid.uuid4())


def test_add_model(driver):
    driver.get('http://localhost:5000')
    driver.set_window_size(1920,1080)
    with test_project() as p:
        with test_dataset(p) as ds:
            with test_featureset(p) as fs:
                driver.refresh()
                proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
                proj_select.select_by_value(str(p.id))


                driver.find_element_by_id('react-tabs-6').click()
                driver.find_element_by_partial_link_text('Create New Model').click()

                model_name = driver.find_element_by_css_selector('[name=modelName]')
                model_name.send_keys(test_model_name)

                driver.find_element_by_class_name('btn-primary').click()

                driver.implicitly_wait(0.2)
                try:
                    status_td = driver.find_element_by_xpath(
                        "//div[contains(text(),'Model training begun')]")

                    driver.implicitly_wait(1)
                    status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
                except:
                    driver.save_screenshot("/tmp/models_fail.png")
                    raise

def test_delete_model(driver):
    driver.get('http://localhost:5000')
    driver.set_window_size(1920,1080)
    with test_project() as p:
        with test_dataset(p) as ds:
            with test_featureset(p) as fs:
                with test_model(fs) as m:
                    driver.refresh()
                    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
                    proj_select.select_by_value(str(p.id))


                    driver.find_element_by_id('react-tabs-6').click()
                    driver.find_element_by_partial_link_text('Delete').click()
                    driver.implicitly_wait(1)
                    status_td = driver.find_element_by_xpath(
                        "//div[contains(text(),'Model successfully deleted')]")
