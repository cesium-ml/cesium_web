import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import uuid
import time
from cesium_app.tests.fixtures import create_test_project


def test_create_project(driver):
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

    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_visible_text(test_proj_name)
    time.sleep(0.1)

    assert driver.find_element_by_css_selector('[name=projectDescription]').\
        get_attribute("value") == "Test Description"

    # Delete project
    driver.find_element_by_partial_link_text('Delete Project').click()
    time.sleep(0.1)


def test_edit_project(driver):
    with create_test_project() as p:
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
    with create_test_project() as p:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_partial_link_text('Delete Project').click()
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Project deleted')]")


def test_main_content_disabled_no_project(driver):
    driver.refresh()

    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    try:
        proj_select.first_selected_option
    except NoSuchElementException:
        pytest.raises(WebDriverException, driver.find_element_by_id('react-tabs-2').click)
    else:
        print("This is not a clean database, so cannot test this functionality.")
