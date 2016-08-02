import pytest
from selenium import webdriver
import uuid


@pytest.fixture(scope="module")
def driver(request):
    from selenium import webdriver

    driver = webdriver.PhantomJS()
    request.addfinalizer(lambda: driver.close())

    return driver


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


def test_edit_project(driver):
    # Update project name and description
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
    # Delete project
    driver.find_element_by_partial_link_text('Delete Project').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Project successfully deleted')]")
