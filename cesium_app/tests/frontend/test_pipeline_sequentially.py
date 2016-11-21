import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import os
from os.path import join as pjoin
import time


def test_pipeline_sequentially(driver):
    driver.get("/")

    # Add new project
    driver.implicitly_wait(1)
    driver.find_element_by_partial_link_text('Or click here to add a new one').click()

    project_name = driver.find_element_by_css_selector('[name=projectName]')
    test_proj_name = str(uuid.uuid4())
    project_name.send_keys(test_proj_name)
    project_desc = driver.find_element_by_css_selector('[name=projectDescription]')
    project_desc.send_keys("Test Description")

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Added new project')]")
    time.sleep(0.1)
    assert test_proj_name in driver.page_source

    # Ensure new project is selected
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_visible_text(test_proj_name)

    # Add new dataset
    test_dataset_name = str(uuid.uuid4())
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Upload new dataset').click()

    dataset_name = driver.find_element_by_css_selector('[name=datasetName]')
    dataset_name.send_keys(test_dataset_name)

    header_file = driver.find_element_by_css_selector('[name=headerFile]')
    header_file.send_keys(pjoin(
        os.path.dirname(os.path.dirname(__file__)), 'data',
        'larger_asas_training_subset_classes_with_metadata.dat'))

    tar_file = driver.find_element_by_css_selector('[name=tarFile]')
    tar_file.send_keys(pjoin(os.path.dirname(os.path.dirname(__file__)), 'data',
                             'larger_asas_training_subset.tar.gz'))

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Successfully uploaded new dataset')]")
    assert test_dataset_name in driver.page_source

    # Generate new feature set
    test_featureset_name = str(uuid.uuid4())
    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()
    # Uncheck LS feats
    driver.find_element_by_xpath("//li[contains(.,'Lomb-Scargle')]").click()
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()

    featureset_name = driver.find_element_by_css_selector('[name=featuresetName]')
    featureset_name.send_keys(test_featureset_name)

    # Ensure dataset from previous step is selected
    dataset_select = Select(driver.find_element_by_css_selector('[name=datasetID]'))
    dataset_select.select_by_visible_text(test_dataset_name)

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature computation begun')]")
    status_td = driver.find_element_by_xpath("//td[contains(text(),'In progress')]")

    driver.implicitly_wait(30)
    status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")

    # Build new model
    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_partial_link_text('Create New Model').click()

    model_select = Select(driver.find_element_by_css_selector('[name=modelType]'))
    model_select.select_by_visible_text('RandomForestClassifier (fast)')

    model_name = driver.find_element_by_css_selector('[name=modelName]')
    test_model_name = str(uuid.uuid4())
    model_name.send_keys(test_model_name)

    # Ensure featureset from previous step is selected
    fset_select = Select(driver.find_element_by_css_selector('[name=featureSet]'))
    fset_select.select_by_visible_text(test_featureset_name)

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(0.5)
    driver.find_element_by_xpath("//div[contains(text(),'Model training begun')]")

    driver.implicitly_wait(15)
    driver.find_element_by_xpath("//td[contains(.,'Completed')]")

    # Predict using dataset and model from this test
    driver.find_element_by_id('react-tabs-8').click()
    driver.find_element_by_partial_link_text('Predict Targets').click()

    # Ensure model from previous step is selected
    model_select = Select(driver.find_element_by_css_selector('[name=modelID]'))
    model_select.select_by_visible_text(test_model_name)

    # Ensure dataset from previous step is selected
    dataset_select = Select(driver.find_element_by_css_selector('[name=datasetID]'))
    dataset_select.select_by_visible_text(test_dataset_name)

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    driver.find_element_by_xpath(
        "//div[contains(text(),'Model predictions begun')]")

    driver.implicitly_wait(10)
    driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
