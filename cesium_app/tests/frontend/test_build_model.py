import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import uuid
import time
import os
from os.path import join as pjoin
from cesium_app.tests.fixtures import (create_test_project, create_test_dataset,
                                       create_test_featureset, create_test_model)


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
        driver.implicitly_wait(0.5)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Model training begun')]")

        driver.implicitly_wait(2)
        status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")
    except:
        driver.save_screenshot("/tmp/models_fail.png")
        raise


def test_build_model_rfc(driver):
    driver.get('/')
    with create_test_project() as p, create_test_featureset(p) as fs:
        _build_model(p.id, 'RandomForestClassifier', driver)


def test_build_model_lsgdc(driver):
    driver.get('/')
    with create_test_project() as p, create_test_featureset(p) as fs:
        _build_model(p.id, 'LinearSGDClassifier', driver)


def test_build_model_lr(driver):
    driver.get('/')
    with create_test_project() as p,\
         create_test_featureset(p, label_type='regr') as fs:
        _build_model(p.id, 'LinearRegressor', driver)


def test_delete_model(driver):
    driver.get('/')
    with create_test_project() as p, create_test_featureset(p) as fs,\
         create_test_model(fs) as m:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))

        driver.find_element_by_id('react-tabs-6').click()
        driver.find_element_by_partial_link_text('Delete').click()
        driver.implicitly_wait(1)
        status_td = driver.find_element_by_xpath(
            "//div[contains(text(),'Model deleted')]")


def test_hyper_param_populate(driver):
    driver.get('/')
    with create_test_project() as p, create_test_featureset(p) as fs, create_test_model(fs) as m:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))

        driver.find_element_by_id('react-tabs-6').click()

        driver.find_element_by_partial_link_text('Create New Model').click()
        driver.find_element_by_partial_link_text('Choose Model Parameters').click()
        model_select = Select(driver.find_element_by_css_selector('[name=modelType]'))
        model_select.select_by_visible_text("RandomForestClassifier")
        driver.implicitly_wait(0.1)
        driver.find_element_by_xpath("//label[contains(text(),'n_estimators')]")
        driver.find_element_by_xpath("//label[contains(text(),'max_features')]")

        model_select.select_by_visible_text("RidgeClassifierCV")
        driver.implicitly_wait(0.1)
        driver.find_element_by_xpath("//label[contains(text(),'alphas')]")
        driver.find_element_by_xpath("//label[contains(text(),'scoring')]")

        model_select.select_by_visible_text("BayesianRidgeRegressor")
        driver.implicitly_wait(0.1)
        driver.find_element_by_xpath("//label[contains(text(),'n_iter')]")
        driver.find_element_by_xpath("//label[contains(text(),'alpha_1')]")


def test_cannot_build_model_unlabeled_data(driver):
    driver.get('/')
    with create_test_project() as p,\
         create_test_featureset(p, label_type='none') as fs:
        driver.refresh()
        proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
        proj_select.select_by_value(str(p.id))

        driver.find_element_by_id('react-tabs-6').click()
        driver.find_element_by_partial_link_text('Create New Model').click()

        model_name = driver.find_element_by_css_selector('[name=modelName]')
        model_name.send_keys(str(uuid.uuid4()))

        driver.find_element_by_class_name('btn-primary').click()

        driver.implicitly_wait(2)
        driver.find_element_by_xpath(
            "//div[contains(.,'Cannot build model for unlabeled feature set.')]")
