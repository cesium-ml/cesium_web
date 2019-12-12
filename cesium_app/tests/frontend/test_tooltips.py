import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def DISABLED_test_tab_tooltips(driver, project):
    driver.get('/')
    driver.refresh()

    ActionChains(driver).move_to_element(
        driver.find_element_by_id('react-tabs-0')).perform()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, "//span[contains(.,'Manage your projects')]")))
    # assert driver.find_element_by_xpath(
    #     "//span[contains(.,'Manage your projects')]"
    # ).is_displayed()

    ActionChains(driver).move_to_element(
        driver.find_element_by_id('react-tabs-2')).perform()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, "//span[contains(.,'Upload your time-series data')]")))
    # time.sleep(1.5)
    # assert driver.find_element_by_xpath(
    #     "//span[contains(.,'Upload your time-series data')]"
    #     ).is_displayed()

    ActionChains(driver).move_to_element(
        driver.find_element_by_id('react-tabs-4')).perform()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, "//span[contains(.,'Generate features from your time-series data')]")))
    # time.sleep(1.5)
    # assert driver.find_element_by_xpath(
    #     "//span[contains(.,'Generate features from your time-series data')]"
    # ).is_displayed()


def DISABLED_test_headerfile_upload_tooltip(driver, project):
    driver.get('/')
    driver.refresh()
    driver.find_element_by_id('react-tabs-2').click()
    driver.find_element_by_partial_link_text('Upload new dataset').click()
    time.sleep(0.2)

    header_file = driver.find_element_by_css_selector('[name="headerFile"]')
    ActionChains(driver).click_and_hold(header_file).perform()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, "//span[contains(.,'filename,label')]")))
    # time.sleep(1)
    # assert driver.find_element_by_xpath(
    #     "//span[contains(.,'filename,label')]"
    # ).is_displayed()


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
