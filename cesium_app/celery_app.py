from celery import Celery
from cesium.celery_app import celery_config

celery_config['CELERY_IMPORTS'].append('cesium_app.celery_tasks')
#celery_config['CELERY_RESULT_DBURI'] = 'db+postgresql://cesium:cesium@localhost/cesium'
#celery_config['CELERY_RESULT_BACKEND'] = 'db+postgresql://cesium:cesium@localhost/cesium'
app = Celery('cesium_app', broker=celery_config['CELERY_BROKER'])
app.config_from_object(celery_config)
