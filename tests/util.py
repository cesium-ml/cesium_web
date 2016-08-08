import uuid
import os
from os.path import join as pjoin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_new_project(driver):
    driver.implicitly_wait(5)
    driver.find_element_by_partial_link_text('Or click here to add a new one').click()

    project_name = driver.find_element_by_css_selector('[name=projectName]')
    test_proj_name = str(uuid.uuid4())
    project_name.send_keys(test_proj_name)
    driver.find_element_by_class_name('btn-primary').click()
    try:
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Successfully added new project')]")
    except:
        driver.save_screenshot("/tmp/util_add_new_proj_fail.png")
        raise


def delete_current_project(driver):
    driver.find_element_by_id('react-tabs-0').click()
    driver.find_element_by_partial_link_text('Delete Project').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Project successfully deleted')]")
    driver.refresh()


def add_dataset(driver):
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Upload new dataset').click()

    dataset_name = driver.find_element_by_css_selector('[name=datasetName]')
    test_dset_name = str(uuid.uuid4())
    dataset_name.send_keys(test_dset_name)

    header_file = driver.find_element_by_css_selector('[name=headerFile]')
    header_file.send_keys(pjoin(os.path.dirname(__file__), 'data/asas_training_subset_classes.dat'))

    tar_file = driver.find_element_by_css_selector('[name=tarFile]')
    tar_file.send_keys(pjoin(os.path.dirname(__file__), 'data/asas_training_subset.tar.gz'))

    driver.find_element_by_class_name('btn-primary').click()
    driver.implicitly_wait(2)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Successfully uploaded new dataset')]")
    assert test_dset_name in driver.page_source


def delete_dataset(driver):
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Delete').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Dataset successfully deleted')]")


def add_featureset(driver):
    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()
    featureset_name = driver.find_element_by_css_selector('[name=featuresetName]')
    test_fset_name = str(uuid.uuid4())
    featureset_name.send_keys(test_fset_name)
    driver.find_element_by_class_name('btn-primary').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature computation begun')]")
    status_td = driver.find_element_by_xpath("//td[contains(text(),'In progress')]")
    driver.implicitly_wait(10)
    status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")


def delete_featureset(driver):
    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Delete').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature set successfully deleted')]")


def add_model(driver):
    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_partial_link_text('Create New Model').click()

    test_model_name = str(uuid.uuid4())
    model_name = driver.find_element_by_css_selector('[name=modelName]')
    model_name.send_keys(test_model_name)

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Model training begun')]")

    try:
        driver.implicitly_wait(2)
        status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
    except:
        driver.save_screenshot("/tmp/util_add_model_fail.png")
        raise


def delete_model(driver):
    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_partial_link_text('Delete').click()
