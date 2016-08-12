import pytest
from selenium import webdriver


@pytest.fixture(scope="module")
def driver(request):
    from selenium import webdriver

    driver = webdriver.PhantomJS()
    request.addfinalizer(lambda: driver.close())

    return driver


def test_front_page(driver):
    driver.get("http://localhost:5000")
    assert 'localhost' in driver.current_url
    assert 'Choose your project here' in driver.find_element_by_tag_name('body').text
