import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin
from util import create_test_project, create_test_dataset,\
    create_test_featureset, create_test_model, create_test_prediction


def test_add_prediction(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs, create_test_model(fs) as m:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))

        driver.find_element_by_id('react-tabs-8').click()
        driver.find_element_by_partial_link_text('Predict Targets').click()

        driver.find_element_by_class_name('btn-primary').click()

        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Model predictions begun')]")

        try:
            driver.implicitly_wait(10)
            status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
        except:
            driver.save_screenshot("/tmp/pred_fail.png")
            raise


def test_click_prediction(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs, create_test_model(fs) as m,\
         create_test_prediction(ds, m):
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-8').click()
        driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
        try:
            import time; time.sleep(1)
            driver.implicitly_wait(1)
            driver.find_element_by_xpath("//td[contains(text(),'Mira')]")
            driver.find_element_by_xpath("//th[contains(text(),'Time Series')]")
        except:
            driver.save_screenshot("/tmp/pred_click_tr_fail.png")
            raise


def test_delete_prediction(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs, create_test_model(fs) as m,\
         create_test_prediction(ds, m):
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-8').click()
        driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
        import time; time.sleep(0.2)
        driver.find_element_by_partial_link_text('Delete').click()
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Prediction deleted')]")
