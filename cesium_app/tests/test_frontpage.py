import pytest
from selenium import webdriver


def test_front_page(driver):
    driver.get("/")
    assert 'localhost' in driver.current_url
    assert 'Choose your project here' in driver.find_element_by_tag_name('body').text
