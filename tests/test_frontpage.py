import pytest
from selenium import webdriver


@pytest.fixture(scope="module")
def driver(request):
    from selenium import webdriver

    driver = webdriver.PhantomJS()
    request.addfinalizer(lambda: driver.close())

    return driver


def test_front_page(driver):
    driver.get("http://localhost:4000")
    assert 'localhost' in driver.current_url
    assert 'Create a new project' in driver.find_element_by_tag_name('body').text


def test_create_project(driver):
    form = driver.find_element_by_css_selector('[data-test-name=newProjectForm]')

    project_name = form.find_element_by_tag_name('input')
    project_name.send_keys('Test Project')

    form.find_element_by_class_name('submitButton').click()

    driver.refresh()
    assert 'Test Project' in driver.page_source
