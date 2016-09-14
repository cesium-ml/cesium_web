#!/usr/bin/env python

import subprocess
import os
import sys
from os.path import join as pjoin
import time
import socket
from tools.supervisor_status import supervisor_status
try:
    import http.client as http
except ImportError:
    import httplib as http

base_dir = os.path.abspath(pjoin(os.path.dirname(__file__), '..'))


def add_test_yaml():
    print('Creating cesium-test.yaml')
    with open('cesium-test.yaml', 'w') as f:
        f.write('database:\n    database: cesium_test\n    user: cesium')


def delete_test_yaml():
    os.remove('cesium-test.yaml')


def clear_db():
    from cesium_app import models
    models.drop_tables()
    models.create_tables()


if __name__ == '__main__':
    add_test_yaml()
    clear_db()
    web_client = subprocess.Popen(['make'], cwd=base_dir)

    print('[test_frontend] Waiting for supervisord to launch all server processes...')

    try:
        timeout = 0
        while ((timeout < 10) and
               (not all([b'RUNNING' in line for line in supervisor_status()]))):
            time.sleep(1)
            timeout += 1

        if timeout == 10:
            print('[test_frontend] Could not launch server processes; terminating')
            sys.exit(-1)

        for timeout in range(10):
            conn = http.HTTPConnection("localhost", 5000)
            try:
                conn.request('HEAD', '/')
                status = conn.getresponse().status
                if status == 200:
                    break
            except socket.error:
                pass
            time.sleep(1)
        else:
            raise socket.error("Could not connect to localhost:5000.")

        if status != 200:
            print('[test_frontend] Server status is {} instead of 200'.format(
                status))
            sys.exit(-1)
        else:
            print('[test_frontend] Verified server availability')

        print('[test_frontend] Launching pytest...')
        test_dir = pjoin(base_dir, 'cesium_app', 'tests')
        status = subprocess.call(['py.test', '--verbose', test_dir])
    except:
        raise
    finally:
        print('[test_frontend] Terminating supervisord...')
        web_client.terminate()
        delete_test_yaml()

    sys.exit(status)
