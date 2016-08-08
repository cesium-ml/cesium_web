# encoding: utf-8

import tornado.web
import tornado.ioloop
import tornado.gen

import json
import requests
import time
import traceback

from distributed import Executor

import joblib
import xarray as xr
from cesium import featurize, build_model, predict, time_series
from cesium_app.config import cfg


IP = '127.0.0.1'
PORT = 63000
PORT_SCHEDULER = 63500


# TODO pass in executor or make class method?
def featurize_task(executor, ts_paths, features_to_use, output_path,
                   custom_script_path=None):
    all_time_series = executor.map(time_series.from_netcdf, ts_paths)
    all_features = executor.map(featurize.featurize_single_ts, all_time_series,
                                features_to_use=features_to_use,
                                custom_script_path=custom_script_path)
    fset = executor.submit(featurize.assemble_featureset, all_features,
                           all_time_series)
    return executor.submit(xr.Dataset.to_netcdf, fset, output_path)


def build_model_task(executor, model_type, model_params, fset_path,
                     output_path, params_to_optimize=None):
    fset = executor.submit(lambda path: xr.open_dataset(path).load(), fset_path)
    model = executor.submit(build_model.build_model_from_featureset,
                            featureset=fset, model_type=model_type,
                            model_options=model_params,
                            params_to_optimize=params_to_optimize)
    return executor.submit(joblib.dump, model, output_path)


def predict_task(executor, ts_paths, features_to_use, model_path, output_path,
                 custom_script_path=None):
    all_time_series = executor.map(time_series.from_netcdf, ts_paths)
    all_features = executor.map(featurize.featurize_single_ts, all_time_series,
                                features_to_use=features_to_use,
                                custom_script_path=custom_script_path)
    fset = executor.submit(featurize.assemble_featureset, all_features,
                           all_time_series)
    model = executor.submit(joblib.load, model_path)
    predset = executor.submit(predict.model_predictions, fset, model)
    return executor.submit(xr.Dataset.to_netcdf, predset, output_path)


class TaskHandler(tornado.web.RequestHandler):
    def get(self, task_id):
        self.write('Querying future id {}'.format(task_id))

    @tornado.gen.coroutine
    def post(self):
        task_data = json.loads(self.request.body.decode('utf-8'))

        try:
            if task_data['type'] == 'featurize':
                future = featurize_task(self.application.executor, **task_data['params'])
            elif task_data['type'] == 'build_model':
                future = build_model_task(self.application.executor, **task_data['params'])
            elif task_data['type'] == 'predict':
                future = predict_task(self.application.executor, **task_data['params'])
            else:
                self.write({'status': 'error',
                            'message': 'Unrecognized task type'})
        except Exception as e:
            trace = traceback.format_exc()
            print(trace)
            self.write({'status': 'error',
                        'message': 'Failed to submit task: {}'.format(trace)})
            self.report_result(None, task_data['metadata'])
        else:
            self.write({
                'status': 'success',
                'data': {'task_id': future.key}
                })

        loop.spawn_callback(self.report_result, future, task_data['metadata'])

    @tornado.gen.coroutine
    def report_result(self, future, metadata):
        try:
            result = yield future._result()
            metadata.update({'status': 'success'})
        except Exception as e:
            trace = traceback.format_exc()
            print(trace)
            metadata.update({'status': 'error',
                             'message': 'Failed to execute task: {}'.format(trace)})
        finally:
            r = requests.post('{}/task_complete'.format(cfg['server']['url']),
                              json=metadata)
            self.write(metadata)


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        loop = kwargs.pop('loop')
        tornado.web.Application.__init__(self, *args, **kwargs)

        self.executor = Executor('{}:{}'.format(IP, PORT_SCHEDULER), loop=loop,
                                 start=False)

        loop.add_future(self.executor._start(), None)


def make_app(loop):
    app = Application([
        (r"/task/([0-9a-z]+)?", TaskHandler),
        (r"/task", TaskHandler),
        ], debug=True, loop=loop)

    return app


if __name__ == "__main__":
    loop = tornado.ioloop.IOLoop.current()

    from distributed import Scheduler
    s = Scheduler(loop=loop)
    s.start(PORT_SCHEDULER)
    print('Task scheduler listening on port {}'.format(PORT_SCHEDULER))

    from distributed import Worker
    w = Worker('127.0.0.1', PORT_SCHEDULER, loop=loop)
    w.start(0)
    print('Single worker activated')

    app = make_app(loop)
    app.listen(PORT)
    print('Task server listening on port {}'.format(PORT))

    print('Starting main loop...')
    loop.start()
