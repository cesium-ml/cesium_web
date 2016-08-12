import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
from util import test_project


def test_create_project(driver):
    driver.set_window_size(1920,1080)

    driver.get("http://localhost:5000")

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
        "//div[contains(text(),'Successfully added new project')]")
    assert test_proj_name in driver.page_source
    assert driver.find_element_by_css_selector('[name=projectDescription]').\
        get_attribute("value") == "Test Description"

    # Delete project
    driver.find_element_by_partial_link_text('Delete Project').click()
    import time; time.sleep(0.1)


def test_edit_project(driver):
    with test_project() as p:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        project_name = driver.find_element_by_css_selector('[name=projectName]')
        project_name.clear()
        test_proj_name = str(uuid.uuid4())
        project_name.send_keys(test_proj_name)
        project_desc = driver.find_element_by_css_selector('[name=projectDescription]')
        project_desc.clear()
        project_desc.send_keys("New Test Description")
        driver.find_element_by_class_name('btn-primary').click()

        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Successfully updated project')]")
        assert driver.find_element_by_css_selector('[name=projectName]').\
            get_attribute("value") == test_proj_name
        assert driver.find_element_by_css_selector('[name=projectDescription]').\
            get_attribute("value") == "New Test Description"


def test_delete_project(driver):
    with test_project() as p:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_partial_link_text('Delete Project').click()
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Project successfully deleted')]")
