import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin
import numpy as np
import numpy.testing as npt
from cesium_app.config import cfg
import json
import requests
from cesium_app.tests.fixtures import (create_test_project, create_test_dataset,
                                       create_test_featureset, create_test_model,
                                       create_test_prediction)


def _add_prediction(proj_id, driver):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))

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


def _click_prediction_row(proj_id, driver):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))
    driver.find_element_by_id('react-tabs-8').click()
    driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()


def _grab_pred_results_table_rows(driver, text_to_look_for):
    driver.implicitly_wait(1)
    td = driver.find_element_by_xpath("//td[contains(text(),'{}')]".format(
        text_to_look_for))
    tr = td.find_element_by_xpath('..')
    table = tr.find_element_by_xpath('..')
    rows = table.find_elements_by_tag_name('tr')
    return rows


def test_add_prediction_rfc(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs, create_test_model(fs) as m:
        _add_prediction(p.id, driver)


def test_pred_results_table_rfc(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs, create_test_model(fs) as m,\
         create_test_prediction(ds, m):
        _click_prediction_row(p.id, driver)
        try:
            rows = _grab_pred_results_table_rows(driver, 'Mira')
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
         create_test_model(fs, model_type='LinearSGDClassifier') as m:
        _add_prediction(p.id, driver)


def test_pred_results_table_lsgdc(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs,\
         create_test_model(fs, model_type='LinearSGDClassifier') as m,\
         create_test_prediction(ds, m):
        _click_prediction_row(p.id, driver)
        try:
            rows = _grab_pred_results_table_rows(driver, 'Mira')
            rows = [row.text for row in rows]
            npt.assert_array_equal(
                ['0 Mira Mira', '1 Classical_Cepheid Classical_Cepheid',
                 '2 Mira Mira', '3 Classical_Cepheid Classical_Cepheid',
                 '4 Mira Mira'],
                rows)
        except:
            driver.save_screenshot("/tmp/pred_click_tr_fail.png")
            raise


def test_add_prediction_rfr(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p, label_type='regr') as ds,\
         create_test_featureset(p, label_type='regr') as fs,\
         create_test_model(fs, model_type='RandomForestRegressor') as m:
        _add_prediction(p.id, driver)


def test_pred_results_table_regr(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p, label_type='regr') as fs,\
         create_test_model(fs, model_type='LinearRegressor') as m,\
         create_test_prediction(ds, m):
        _click_prediction_row(p.id, driver)
        try:
            rows = _grab_pred_results_table_rows(driver, '3.4')
            rows = [[float(el) for el in row.text.split(' ')] for row in rows]
            npt.assert_array_almost_equal(
                [[0.0, 2.2, 2.2000000000000006], [1.0, 3.4, 3.4000000000000004],
                 [2.0, 4.4, 4.400000000000001], [3.0, 2.2, 2.1999999999999993],
                 [4.0, 3.1, 3.099999999999999]],
                rows)
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
        driver.implicitly_wait(1)
        driver.find_element_by_xpath("//td[contains(text(),'Completed')]").click()
        time.sleep(0.2)
        driver.find_element_by_partial_link_text('Delete').click()
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Prediction deleted')]")


def _click_download(proj_id, driver):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))
    driver.find_element_by_id('react-tabs-8').click()
    driver.implicitly_wait(1)
    driver.find_element_by_partial_link_text('Download').click()
    time.sleep(0.5)


def test_download_prediction_csv_class(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs,\
         create_test_model(fs, model_type='LinearSGDClassifier') as m,\
         create_test_prediction(ds, m):
        _click_download(p.id, driver)
        assert os.path.exists('/tmp/cesium_prediction_results.csv')
        try:
            npt.assert_equal(
                np.genfromtxt('/tmp/cesium_prediction_results.csv', dtype='str'),
                ['ts_name,label,prediction',
                 '0,Mira,Mira',
                 '1,Classical_Cepheid,Classical_Cepheid',
                 '2,Mira,Mira',
                 '3,Classical_Cepheid,Classical_Cepheid',
                 '4,Mira,Mira'])
        finally:
            os.remove('/tmp/cesium_prediction_results.csv')


def test_download_prediction_csv_regr(driver):
    driver.get('/')
    with create_test_project() as p, create_test_dataset(p, label_type='regr') as ds,\
         create_test_featureset(p, label_type='regr') as fs,\
         create_test_model(fs, model_type='LinearRegressor') as m,\
         create_test_prediction(ds, m):
        _click_download(p.id, driver)
        assert os.path.exists('/tmp/cesium_prediction_results.csv')
        try:
            results = np.genfromtxt('/tmp/cesium_prediction_results.csv',
                                    dtype='str', delimiter=',')
            npt.assert_equal(results[0],
                             ['ts_name', 'label', 'prediction'])
            npt.assert_array_almost_equal(
                [[float(e) for e in row] for row in results[1:]],
                [[0, 2.2, 2.2],
                 [1, 3.4, 3.4],
                 [2, 4.4, 4.4],
                 [3, 2.2, 2.2],
                 [4, 3.1, 3.1]])
        finally:
            os.remove('/tmp/cesium_prediction_results.csv')


def test_predict_specific_ts_name():
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs, create_test_model(fs) as m:
        ts_data = [[1, 2, 3, 4], [32.2, 53.3, 32.3, 32.52], [0.2, 0.3, 0.6, 0.3]]
        impute_kwargs = {'strategy': 'constant', 'value': None}
        data = {'datasetID': ds.id,
                'ts_names': ['217801'],
                'modelID': m.id}
        response = requests.post('{}/predictions'.format(cfg['server']['url']),
                                 data=json.dumps(data)).json()
        assert response['status'] == 'success'

        n_secs = 0
        while n_secs < 5:
            pred_info = requests.get('{}/predictions/{}'.format(
                cfg['server']['url'], response['data']['id'])).json()
            if pred_info['status'] == 'success' and pred_info['data']['finished']:
                assert isinstance(pred_info['data']['results']['217801']
                                  ['features']['total_time'],
                                  float)
                assert 'Mira' in pred_info['data']['results']['217801']['prediction']
                break
            n_secs += 1
            time.sleep(1)
        else:
            raise Exception('test_predict_specific_ts_name timed out')
