import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import os
from os.path import join as pjoin

test_dataset_name = str(uuid.uuid4())


def test_add_new_dataset(driver, project):
    driver.get("/")

    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))
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


def test_dataset_info_display(driver, project, dataset):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))
    driver.find_element_by_id('react-tabs-2').click()

    driver.find_element_by_xpath("//td[contains(text(),'{}')]".format(dataset.name)).click()
    assert driver.find_element_by_xpath("//th[contains(text(),'Time Series "
                                        "File Names')]").is_displayed()
    assert driver.find_element_by_xpath("//th[contains(text(),'Meta "
                                        "Features')]").is_displayed()


def test_delete_dataset(driver, project, dataset):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Delete').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Dataset deleted')]")
