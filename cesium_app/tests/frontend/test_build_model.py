import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin


def _build_model(proj_id, model_type, driver):
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(proj_id))

    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_partial_link_text('Create New Model').click()

    model_select = Select(driver.find_element_by_css_selector('[name=modelType]'))
    model_select.select_by_visible_text(model_type)

    model_name = driver.find_element_by_css_selector('[name=modelName]')
    test_model_name = str(uuid.uuid4())
    model_name.send_keys(test_model_name)

    driver.find_element_by_class_name('btn-primary').click()

    try:
        driver.wait_for_xpath("//div[contains(text(), 'Model training begun')]")
        driver.wait_for_xpath("//td[contains(text(), 'Completed')]", 10)
    except:
        driver.save_screenshot("/tmp/models_fail.png")
        raise


@pytest.mark.parametrize('featureset__name, model_type',
                         [('class', 'RandomForestClassifier (fast)'),
                          ('class', 'LinearSGDClassifier'),
                          ('regr', 'LinearRegressor')])
def test_build_model(driver, project, featureset, model_type):
    driver.get('/')
    _build_model(project.id, model_type, driver)


def test_delete_model(driver, project, featureset, model):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_partial_link_text('Delete').click()
    status_td = driver.wait_for_xpath(
        "//div[contains(text(),'Model deleted')]")


def test_hyper_param_populate(driver, project, featureset, model):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-6').click()

    driver.find_element_by_partial_link_text('Create New Model').click()
    driver.find_element_by_partial_link_text('Choose Model Parameters').click()
    model_select = Select(driver.find_element_by_css_selector('[name=modelType]'))
    model_select.select_by_visible_text("RandomForestClassifier (fast)")
    driver.wait_for_xpath("//label[contains(text(),'n_estimators')]")
    driver.wait_for_xpath("//label[contains(text(),'max_features')]")

    model_select.select_by_visible_text("RidgeClassifierCV")
    driver.wait_for_xpath("//label[contains(text(),'alphas')]")
    driver.wait_for_xpath("//label[contains(text(),'scoring')]")

    model_select.select_by_visible_text("BayesianRidgeRegressor")
    driver.wait_for_xpath("//label[contains(text(),'n_iter')]")
    driver.wait_for_xpath("//label[contains(text(),'alpha_1')]")


@pytest.mark.parametrize('featureset__name', ['unlabeled'])
def test_cannot_build_model_unlabeled_data(driver, project, featureset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_partial_link_text('Create New Model').click()

    model_name = driver.find_element_by_css_selector('[name=modelName]')
    model_name.send_keys(str(uuid.uuid4()))

    driver.find_element_by_class_name('btn-primary').click()

    driver.wait_for_xpath(
        "//div[contains(.,'Cannot build model for unlabeled feature set.')]")


@pytest.mark.parametrize('featureset__name, model_type',
                         [('class', 'RandomForestClassifier (fast)')])
def test_model_info_display(driver, project, featureset, model_type):
    driver.refresh()
    _build_model(project.id, model_type, driver)

    driver.wait_for_xpath("//td[contains(text(), 'Completed')]").click()
    time.sleep(0.5)
    assert driver.wait_for_xpath("//th[contains(text(),'Model Type')]")\
                 .is_displayed()
    assert driver.wait_for_xpath("//th[contains(text(),"
                                 "'Hyperparameters')]").is_displayed()
    assert driver.wait_for_xpath("//th[contains(text(),"
                                 "'train_score')]").is_displayed()
    assert driver.wait_for_xpath("//canvas[@class='chartjs-render-monitor']")\
                 .is_displayed()
