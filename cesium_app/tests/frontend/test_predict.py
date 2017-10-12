import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin
import numpy as np
import numpy.testing as npt
import pandas as pd
import json


def _add_prediction(proj_id, driver):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))

    driver.find_element_by_id('react-tabs-8').click()
    driver.find_element_by_partial_link_text('Predict Targets').click()

    driver.find_element_by_class_name('btn-primary').click()

    driver.wait_for_xpath("//div[contains(text(),'Model predictions begun')]")

    try:
        driver.wait_for_xpath("//td[contains(text(),'Completed')]", 30)
    except:
        driver.save_screenshot("/tmp/pred_fail.png")
        raise


def _click_prediction_row(proj_id, driver):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))
    driver.find_element_by_id('react-tabs-8').click()
    driver.wait_for_xpath("//td[contains(text(), 'Completed')]").click()


def _grab_pred_results_table_rows(driver, text_to_look_for):
    td = driver.wait_for_xpath("//td[contains(text(),'{}')]".format(
        text_to_look_for))
    tr = td.find_element_by_xpath('..')
    table = tr.find_element_by_xpath('..')
    rows = table.find_elements_by_tag_name('tr')
    return rows


@pytest.mark.parametrize('featureset__name, model__type',
                         [('class', 'RandomForestClassifier'),
                          ('class', 'LinearSGDClassifier'),
                          ('regr', 'RandomForestRegressor')])
def test_add_prediction(driver, project, dataset, featureset, model):
    driver.get('/')
    _add_prediction(project.id, driver)


def test_pred_results_table_rfc(driver, project, dataset, featureset, model,
                                prediction):
    driver.get('/')
    _click_prediction_row(project.id, driver)
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


@pytest.mark.parametrize('model__type', ['LinearSGDClassifier'])
def test_pred_results_table_lsgdc(driver, project, dataset, featureset, model,
                                  prediction):
    driver.get('/')
    _click_prediction_row(project.id, driver)
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


@pytest.mark.parametrize('featureset__name, model__type', [('regr', 'LinearRegressor')])
def test_pred_results_table_regr(driver, project, dataset, featureset, model,
                                 prediction):
    driver.get('/')
    _click_prediction_row(project.id, driver)
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


@pytest.mark.parametrize('dataset__name', ['unlabeled'])
def test_pred_results_table_unlabeled(driver, project, dataset, featureset, model):
    driver.get('/')
    _add_prediction(project.id, driver)
    _click_prediction_row(project.id, driver)
    try:
        rows = _grab_pred_results_table_rows(driver, 'Mira')
        for row in rows:
            probs = [float(v.text)
                     for v in row.find_elements_by_tag_name('td')[2::2]]
            assert sorted(probs, reverse=True) == probs
        driver.find_element_by_xpath("//th[contains(text(),'Time Series')]")
    except:
        driver.save_screenshot("/tmp/pred_click_tr_fail.png")
        raise


def test_delete_prediction(driver, project, dataset, featureset, model,
                           prediction):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))
    driver.find_element_by_id('react-tabs-8').click()
    driver.wait_for_xpath("//td[contains(text(),'Completed')]").click()
    driver.wait_for_xpath('//*[contains(text(), "Delete")]').click()
    status_td = driver.wait_for_xpath(
        "//div[contains(text(),'Prediction deleted')]")


def _click_download(proj_id, driver):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))
    driver.find_element_by_id('react-tabs-8').click()
    driver.wait_for_xpath("//a[text()='Download']").click()
    time.sleep(0.5)


@pytest.mark.parametrize('model__type', ['LinearSGDClassifier'])
def test_download_prediction_csv_class(driver, project, dataset, featureset,
                                       model, prediction):
    driver.get('/')
    _click_download(project.id, driver)
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


@pytest.mark.parametrize('model__type', ['LinearSGDClassifier'])
def test_download_prediction_csv_class_unlabeled(driver, project, unlabeled_prediction):
    driver.get('/')
    _click_download(project.id, driver)
    assert os.path.exists('/tmp/cesium_prediction_results.csv')
    try:
        result = np.genfromtxt('/tmp/cesium_prediction_results.csv', dtype='str')
        assert result[0] == 'ts_name,prediction'
        assert all([el[0].isdigit() and el[1] == ',' and el[2:] in
                    ['Mira', 'Classical_Cepheid'] for el in result[1:]])
    finally:
        os.remove('/tmp/cesium_prediction_results.csv')


def test_download_prediction_csv_class_prob(driver, project, dataset,
                                            featureset, model, prediction):
    driver.get('/')
    _click_download(project.id, driver)
    assert os.path.exists('/tmp/cesium_prediction_results.csv')
    try:
        result = pd.read_csv('/tmp/cesium_prediction_results.csv')
        npt.assert_array_equal(result.ts_name, np.arange(5))
        npt.assert_array_equal(result.label, ['Mira', 'Classical_Cepheid',
                                              'Mira', 'Classical_Cepheid',
                                              'Mira'])
        pred_probs = result[['Classical_Cepheid', 'Mira']]
        npt.assert_array_equal(np.argmax(pred_probs.values, axis=1),
                               [1, 0, 1, 0, 1])
        assert (pred_probs.values >= 0.0).all()
    finally:
        os.remove('/tmp/cesium_prediction_results.csv')


@pytest.mark.parametrize('featureset__name, model__type', [('regr', 'LinearRegressor')])
def test_download_prediction_csv_regr(driver, project, dataset, featureset, model, prediction):
    driver.get('/')
    _click_download(project.id, driver)
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


def test_predict_specific_ts_name(driver, project, dataset, featureset, model):
    ts_data = [[1, 2, 3, 4], [32.2, 53.3, 32.3, 32.52], [0.2, 0.3, 0.6, 0.3]]
    impute_kwargs = {'strategy': 'constant', 'value': None}
    data = {'datasetID': dataset.id,
            'ts_names': ['217801'],
            'modelID': model.id}
    response = driver.request(
        'POST', '{}/predictions'.format(driver.server_url),
        data=json.dumps(data)).json()
    assert response['status'] == 'success'

    driver.request('GET', f'{driver.server_url}')  # ensure login

    for i in range(10):
        pred_info = driver.request('GET', '{}/predictions/{}'.format(
            driver.server_url, response['data']['id'])).json()
        if pred_info['status'] == 'success' and pred_info['data']['finished']:
            assert isinstance(pred_info['data']['results']['217801']
                              ['features']['total_time'],
                              float)
            assert 'Mira' in pred_info['data']['results']['217801']['prediction']
            break
        time.sleep(1)
    else:
        raise Exception('test_predict_specific_ts_name timed out')
