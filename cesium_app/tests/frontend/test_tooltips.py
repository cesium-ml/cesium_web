import pytest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from cesium_app.tests.fixtures import create_test_project

def test_tab_tooltips(driver):
    driver.get('/')
    with create_test_project() as p:
        driver.refresh()

        hover = ActionChains(driver).move_to_element(
            driver.find_element_by_id('react-tabs-0'))
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(text(),'Manage your projects')]"
        ).is_displayed()

        hover = ActionChains(driver).move_to_element(
            driver.find_element_by_id('react-tabs-2'))
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(text(),'Upload your time-series data')]"
            ).is_displayed()

        hover = ActionChains(driver).move_to_element(
            driver.find_element_by_id('react-tabs-4'))
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(text(),'Generate features from your time-series data')]"
        ).is_displayed()


def test_file_upload_tooltips(driver):
    driver.get('/')
    with create_test_project() as p:
        driver.refresh()
        driver.find_element_by_id('react-tabs-2').click()
        driver.find_element_by_partial_link_text('Upload new dataset').click()

        header_file = driver.find_element_by_css_selector('[name=headerFile]')
        hover = ActionChains(driver).move_to_element(header_file)
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(.,'filename,target')]"
        ).is_displayed()

        tar_file = driver.find_element_by_css_selector('[name=tarFile]')
        hover = ActionChains(driver).move_to_element(tar_file)
        hover.perform()
        time.sleep(1)
        assert driver.find_element_by_xpath(
            "//span[contains(.,'Each file in tarball should be formatted as follows')]"
        ).is_displayed()
