# encoding: utf-8

import tornado.web
import tornado.ioloop
import tornado.gen

import json
import time

from distributed import Executor


IP = '127.0.0.1'
PORT = 63000
PORT_SCHEDULER = 63500



def my_task(n):
    print("My task: running")
    time.sleep(n)
    print("My task done")
    return n


class TaskHandler(tornado.web.RequestHandler):
    def get(self, task_id):
        self.write('Querying task id {}'.format(task_id))

    @tornado.gen.coroutine
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        print('--- Begin Request ---')
        print(data)
        print('--- End Request ---')

        try:
            task = self.application.executor.submit(my_task, 2, pure=False)
        except Exception as e:
            print('Exception raised while submitting task:')
            print(e)
            self.write({'status': 'error',
                        'message': 'Failed to submit task: {}'.format(e)})
        else:
            self.write({
                'status': 'success',
                'data': {'task_id': task.key}
                })

        loop.spawn_callback(self.report_result, task)

    @tornado.gen.coroutine
    def report_result(self, task):
        result = yield task._result()
        print("<Post result to db etc. on success here>")
        print("Result is: {}".format(result))
        print("---")


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        loop = kwargs.pop('loop')
        tornado.web.Application.__init__(self, *args, **kwargs)

        self.executor = Executor('{}:{}'.format(IP, PORT_SCHEDULER),
                                 loop=loop, start=False)

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
