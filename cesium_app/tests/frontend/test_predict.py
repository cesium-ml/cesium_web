import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin
import numpy.testing as npt
from cesium_app.tests.fixtures import (create_test_project, create_test_dataset,
                                       create_test_featureset, create_test_model,
                                       create_test_prediction)


def test_add_prediction_rfc(driver):
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
            driver.implicitly_wait(30)
            status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
        except:
            driver.save_screenshot("/tmp/pred_fail.png")
            raise


def test_pred_results_table_rfc(driver):
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
            driver.implicitly_wait(1)
            td = driver.find_element_by_xpath("//td[contains(text(),'Mira')]")
            tr = td.find_element_by_xpath('..')
            table = tr.find_element_by_xpath('..')
            rows = table.find_elements_by_tag_name('tr')
            for row in rows:
                probs = [float(v.text)
                         for v in row.find_elements_by_tag_name('td')[3::2]]
                assert sorted(probs, reverse=True) == probs
            driver.find_element_by_xpath("//th[contains(text(),'Time Series')]")
        except:
            driver.save_screenshot("/tmp/pred_click_tr_fail.png")
            raise


def test_add_prediction_lsgdc(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs,\
         create_test_model(fs, type='LinearSGDClassifier') as m:
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
            driver.implicitly_wait(30)
            status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
        except:
            driver.save_screenshot("/tmp/pred_fail.png")
            raise


def test_pred_results_table_lsgdc(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs,\
         create_test_model(fs, type='LinearSGDClassifier') as m,\
         create_test_prediction(ds, m):
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-8').click()
        driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
        try:
            driver.implicitly_wait(1)
            td = driver.find_element_by_xpath("//td[contains(text(),'Mira')]")
            tr = td.find_element_by_xpath('..')
            table = tr.find_element_by_xpath('..')
            rows = table.find_elements_by_tag_name('tr')
            fname_true_class = [row.text.split(' ')[:2] for row in rows]
            npt.assert_array_equal(
                [['0', 'Mira'], ['1', 'Classical_Cepheid'], ['2', 'Mira'],
                 ['3', 'Classical_Cepheid'], ['4', 'Mira']],
                fname_true_class)
        except:
            driver.save_screenshot("/tmp/pred_click_tr_fail.png")
            raise


def test_add_prediction_rfr(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p, type='regr') as ds,\
         create_test_featureset(p, type='regr') as fs,\
         create_test_model(fs, type='RandomForestRegressor') as m:
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
            driver.implicitly_wait(30)
            status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
        except:
            driver.save_screenshot("/tmp/pred_fail.png")
            raise


def test_pred_results_table_regr(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p, type='regr') as fs,\
         create_test_model(fs, type='RandomForestRegressor') as m,\
         create_test_prediction(ds, m):
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))
        driver.find_element_by_id('react-tabs-8').click()
        driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
        try:
            driver.implicitly_wait(1)
            td = driver.find_element_by_xpath("//td[contains(text(),'3.4')]")
            tr = td.find_element_by_xpath('..')
            table = tr.find_element_by_xpath('..')
            rows = table.find_elements_by_tag_name('tr')
            fname_true_target = [row.text.split(' ')[:2] for row in rows]
            npt.assert_array_equal(
                [['0', '2.2'], ['1', '3.4'], ['2', '4.4'], ['3', '2.2'], ['4', '3.1']],
                fname_true_target)
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
