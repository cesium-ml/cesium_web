from celery import Celery
from cesium.celery_app import celery_config

celery_config['CELERY_IMPORTS'].append('cesium_app.celery_tasks')
app = Celery('cesium_app', broker=celery_config['CELERY_BROKER'])
app.config_from_object(celery_config)
