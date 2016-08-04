import pytest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import uuid
import time
import os
from os.path import join as pjoin
import util


def test_add_prediction(driver):
    driver.get('http://localhost:5000')
    driver.set_window_size(1920, 1080)
    util.create_new_project(driver)
    util.add_dataset(driver)
    util.add_featureset(driver)
    util.add_model(driver)

    driver.find_element_by_id('react-tabs-8').click()
    driver.find_element_by_partial_link_text('Predict Targets').click()

    driver.find_element_by_class_name('btn-primary').click()

    driver.save_screenshot("/tmp/preds_after_click.png")
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Model predictions begun')]")
    driver.save_screenshot("/tmp/preds_after_click2.png")

    try:
        driver.implicitly_wait(10)
        status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
    except:
        driver.save_screenshot("/tmp/pred_fail.png")
        raise


# THE FOLLOWING DOES NOT WORK WITH PHANTOM JS
# def test_click_prediction(driver):
#     driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
#     try:
#         import time; time.sleep(1)
#         driver.implicitly_wait(1)
#         driver.find_element_by_xpath("//td[contains(text(),'Mira')]")
#         driver.find_element_by_xpath("//th[contains(text(),'Time Series')]")
#     except:
#         driver.save_screenshot("/tmp/pred_click_tr_fail.png")
#         print(driver.get_log("client"))
#         raise


def test_delete_prediction(driver):
    driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
    import time; time.sleep(3)
    driver.find_element_by_partial_link_text('Delete').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Prediction successfully deleted')]")

    util.delete_dataset(driver)
    util.delete_featureset(driver)
    util.delete_model(driver)
    util.delete_current_project(driver)
