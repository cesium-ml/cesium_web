'''Test fixture configuration.'''

import pytest
import os
import pathlib
import shutil
from pytest_factoryboy import register, LazyFixture
from baselayer.app.config import load_config
from baselayer.app.test_util import (driver, MyCustomWebDriver, reset_state,
                                     set_server_url)
from cesium_app import models
from cesium_app.tests.fixtures import (TMP_DIR, ProjectFactory, DatasetFactory,
                                       FeaturesetFactory, ModelFactory,
                                       PredictionFactory)


print('Loading test configuration from test_config.yaml')
basedir = pathlib.Path(os.path.dirname(__file__))/'../..'
cfg = load_config([basedir/'test_config.yaml'])
set_server_url(f'http://localhost:{cfg["ports:app"]}')
print('Setting test database to:', cfg['database'])
models.init_db(**cfg['database'])


@pytest.fixture(scope='session', autouse=True)
def delete_temporary_files(request):
    def teardown():
        shutil.rmtree(TMP_DIR, ignore_errors=True)
    request.addfinalizer(teardown)


register(ProjectFactory)
register(DatasetFactory)
register(DatasetFactory, "unlabeled_dataset", name="unlabeled")
register(FeaturesetFactory)
register(ModelFactory)
register(PredictionFactory)
register(PredictionFactory, "unlabeled_prediction",
         dataset=LazyFixture("unlabeled_dataset"))
