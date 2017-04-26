from cesium_app.tests.fixtures import (create_test_project, create_test_dataset,
                                       create_test_featureset, create_test_model)
from ..conftest import cfg
import json


def test_predict_raw_data(driver):
    with create_test_project() as p, create_test_dataset(p) as ds,\
         create_test_featureset(p) as fs, create_test_model(fs) as m:
        ts_data = [[1, 2, 3, 4], [32.2, 53.3, 32.3, 32.52], [0.2, 0.3, 0.6, 0.3]]
        impute_kwargs = {'strategy': 'constant', 'value': None}
        query_string = ('{}/predict_raw_data?ts_data={}'
                        '&modelID={}&impute_kwargs={}').format(
                            cfg['server:url'], json.dumps(ts_data),
                            json.dumps(m.id), json.dumps(impute_kwargs))
        response = driver.request('POST', query_string).json()
        assert response['status'] == 'success'
        assert response['data']['0']['features']['total_time'] == 3.0
        assert 'Mira' in response['data']['0']['prediction']
