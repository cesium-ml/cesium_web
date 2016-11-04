import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import os
from os.path import join as pjoin
from cesium_app.tests.fixtures import create_test_project, create_test_dataset

test_dataset_name = str(uuid.uuid4())


def test_add_new_dataset(driver):
    driver.get("/")

    with create_test_project() as p:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-2').click()
        driver.find_element_by_partial_link_text('Upload new dataset').click()

        dataset_name = driver.find_element_by_css_selector('[name=datasetName]')
        dataset_name.send_keys(test_dataset_name)

        header_file = driver.find_element_by_css_selector('[name=headerFile]')
        header_file.send_keys(pjoin(os.path.dirname(os.path.dirname(__file__)), 'data',
                                    'asas_training_subset_classes.dat'))

        tar_file = driver.find_element_by_css_selector('[name=tarFile]')
        tar_file.send_keys(pjoin(os.path.dirname(os.path.dirname(__file__)), 'data',
                                 'asas_training_subset.tar.gz'))

        driver.find_element_by_class_name('btn-primary').click()

        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Successfully uploaded new dataset')]")
        assert test_dataset_name in driver.page_source


def test_dataset_info_display(driver):
    with create_test_project() as p, create_test_dataset(p) as ds:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-2').click()

        driver.find_element_by_xpath("//td[contains(text(),'{}')]".format(ds.name)).click()
        assert driver.find_element_by_xpath("//th[contains(text(),'Time Series "
                                            "File Names')]").is_displayed()
        assert driver.find_element_by_xpath("//th[contains(text(),'Meta "
                                            "Features')]").is_displayed()


def test_delete_dataset(driver):
    with create_test_project() as p, create_test_dataset(p) as ds:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-2').click()
        driver.find_element_by_partial_link_text('Delete').click()
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Dataset deleted')]")
        assert test_dataset_name not in driver.page_source
