import pytest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time


def test_tab_tooltips(driver, project):
    driver.get('/')
    driver.refresh()

    hover = ActionChains(driver).move_to_element(
        driver.find_element_by_id('react-tabs-0'))
    hover.perform()
    time.sleep(1.5)
    assert driver.find_element_by_xpath(
        "//span[contains(text(),'Manage your projects')]"
    ).is_displayed()

    hover = ActionChains(driver).move_to_element(
        driver.find_element_by_id('react-tabs-2'))
    hover.perform()
    time.sleep(1.5)
    assert driver.find_element_by_xpath(
        "//span[contains(text(),'Upload your time-series data')]"
        ).is_displayed()

    hover = ActionChains(driver).move_to_element(
        driver.find_element_by_id('react-tabs-4'))
    hover.perform()
    time.sleep(1.5)
    assert driver.find_element_by_xpath(
        "//span[contains(text(),'Generate features from your time-series data')]"
    ).is_displayed()


def test_headerfile_upload_tooltip(driver, project):
    driver.get('/')
    driver.refresh()
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Upload new dataset').click()
    time.sleep(0.2)

    header_file = driver.find_element_by_css_selector('[name="headerFile"]')
    hover = ActionChains(driver).click_and_hold(header_file)
    hover.perform()
    time.sleep(1)
    assert driver.find_element_by_xpath(
        "//span[contains(.,'filename,label')]"
    ).is_displayed()


def DISABLED_test_tarfile_upload_tooltip(driver, project):
    driver.get('/')
    driver.refresh()
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Upload new dataset').click()
    time.sleep(0.2)

    tar_file = driver.find_element_by_css_selector('[name="tarFile"]')
    hover = ActionChains(driver).click_and_hold(tar_file)
    hover.perform()
    time.sleep(1)
    assert driver.find_element_by_xpath(
        "//span[contains(.,'Each file in tarball should be formatted as follows')]"
    ).is_displayed()
