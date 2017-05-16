import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import uuid
import os
import time
from os.path import join as pjoin


test_featureset_name = str(uuid.uuid4())


def test_add_new_featureset(driver, project, dataset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()

    featureset_name = driver.find_element_by_css_selector('[name=featuresetName]')
    featureset_name.send_keys(test_featureset_name)

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature computation begun')]")
    status_td = driver.find_element_by_xpath("//td[contains(text(),'In progress')]")

    driver.implicitly_wait(30)
    status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")


def test_featurize_unlabeled(driver, project, dataset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()

    featureset_name = driver.find_element_by_css_selector('[name=featuresetName]')
    featureset_name.send_keys(test_featureset_name)

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature computation begun')]")
    status_td = driver.find_element_by_xpath("//td[contains(text(),'In progress')]")

    driver.implicitly_wait(30)
    status_td = driver.find_element_by_xpath("//td[contains(text(),'Completed')]")


def test_check_uncheck_features(driver, project, dataset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()
    driver.find_element_by_xpath("//li[contains(text(),'General')]").click()

    amplitude = driver.find_element_by_css_selector('[name=amplitude]')
    assert amplitude.get_attribute('value') == 'true'
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    time.sleep(0.3)
    assert amplitude.get_attribute('value') == 'false'
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    time.sleep(0.1)
    assert amplitude.get_attribute('value') == 'true'

    driver.find_element_by_xpath("//li[contains(.,'Cadence')]").click()
    n_epochs = driver.find_element_by_css_selector('[name=n_epochs]')
    assert n_epochs.get_attribute('value') == 'true'
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    time.sleep(0.1)
    assert n_epochs.get_attribute('value') == 'false'

    driver.find_element_by_xpath("//li[contains(.,'Lomb-Scargle')]").click()
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    assert driver.find_element_by_css_selector(
        '[name=fold2P_slope_10percentile]').get_attribute('value') == 'false'


def test_check_uncheck_tags(driver, project, dataset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()
    driver.find_element_by_partial_link_text('Filter By Tag').click()
    driver.find_element_by_xpath("//li[contains(text(),'General')]").click()

    driver.find_element_by_css_selector('[name=amplitude]')
    driver.find_element_by_css_selector('[label=Astronomy]').click()
    time.sleep(0.1)
    driver.find_element_by_css_selector('[label=General]').click()
    time.sleep(0.1)
    with pytest.raises(NoSuchElementException):
        driver.find_element_by_css_selector('[name=amplitude]').click()

    driver.find_element_by_css_selector('[label=General]').click()
    driver.implicitly_wait(1)
    driver.find_element_by_css_selector('[name=amplitude]')


def test_feature_descriptions_displayed(driver, project, dataset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()
    driver.find_element_by_xpath("//li[contains(text(),'General')]").click()

    driver.implicitly_wait(0.5)
    driver.find_element_by_xpath(
        "//div[contains(.,'Half the difference between the maximum and "
        "minimum magnitude.')]")


def test_cannot_compute_zero_features(driver, project, dataset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Compute New Features').click()
    driver.find_element_by_xpath("//li[contains(text(),'General')]").click()

    amplitude = driver.find_element_by_css_selector('[name=amplitude]')
    assert amplitude.get_attribute('value') == 'true'
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    time.sleep(0.1)
    assert amplitude.get_attribute('value') == 'false'

    driver.find_element_by_xpath("//li[contains(.,'Cadence')]").click()
    n_epochs = driver.find_element_by_css_selector('[name=n_epochs]')
    assert n_epochs.get_attribute('value') == 'true'
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    time.sleep(0.1)
    assert n_epochs.get_attribute('value') == 'false'

    driver.find_element_by_xpath("//li[contains(.,'Lomb-Scargle')]").click()
    driver.find_element_by_partial_link_text('Check/Uncheck All').click()
    assert driver.find_element_by_css_selector(
        '[name=fold2P_slope_10percentile]').get_attribute('value') == 'false'

    featureset_name = driver.find_element_by_css_selector('[name=featuresetName]')
    featureset_name.send_keys(test_featureset_name)

    driver.find_element_by_class_name('btn-primary').click()

    driver.implicitly_wait(1)
    driver.find_element_by_xpath(
        "//div[contains(.,'At least one feature must be selected')]")


def test_plot_features(driver, project, dataset, featureset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()

    driver.implicitly_wait(1)
    driver.find_element_by_xpath("//td[contains(text(),'{}')]".format(featureset.name)).click()
    driver.implicitly_wait(1)
    driver.find_element_by_xpath("//b[contains(text(),'Please wait while we load your plotting data...')]")

    driver.implicitly_wait(3)
    driver.find_element_by_css_selector("[class=bk-plotdiv]")


def test_delete_featureset(driver, project, dataset, featureset):
    driver.get('/')
    driver.refresh()
    proj_select = Select(driver.find_element_by_css_selector('[name=project]'))
    proj_select.select_by_value(str(project.id))

    driver.find_element_by_id('react-tabs-4').click()
    driver.find_element_by_partial_link_text('Delete').click()
    driver.implicitly_wait(1)
    status_td = driver.find_element_by_xpath(
        "//div[contains(text(),'Feature set deleted')]")
    try:
        el = driver.find_element_by_xpath(
            "//td[contains(text(),'{}')]".format(test_featureset_name))
    except NoSuchElementException:
        pass
    else:
        raise Exception("Featureset still present in table after delete.")
