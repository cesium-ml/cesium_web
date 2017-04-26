#!/usr/bin/env python

import sys
import os
import pathlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import subprocess
from os.path import join as pjoin
import time
import socket
from tools.supervisor_status import supervisor_status
try:
    import http.client as http
except ImportError:
    import httplib as http

from cesium_app.model_util import clear_tables

TEST_CONFIG = '_cesium_test.yaml'


base_dir = os.path.abspath(pjoin(os.path.dirname(__file__), '..'))
if len(sys.argv) > 1:
    test_spec = sys.argv[1]
else:
    test_spec = pjoin(base_dir, 'cesium_app', 'tests')


def add_test_yaml():
    print('Creating {}'.format('_cesium_test.yaml'))

    from textwrap import dedent
    with open(TEST_CONFIG, 'w') as f:
        f.write(dedent('''
            database:
                database: cesium_test
                user: cesium

            server:
                url: http://localhost:5000
                multi_user: True
                auth:
                  debug_login: True
                  google_oauth2_key:
                  google_oauth2_secret:

        '''))


def delete_test_yaml():
    os.remove(TEST_CONFIG)


if __name__ == '__main__':
    add_test_yaml()

    # Initialize the test database connection
    from cesium_app.tests.conftest import init_db
    init_db()

    clear_tables()

    web_client = subprocess.Popen(['make', 'testrun'], cwd=base_dir)

    print('[test_frontend] Waiting for supervisord to launch all server processes...')

    try:
        timeout = 0
        while ((timeout < 30) and
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

        print('[test_frontend] Launching pytest on {}...'.format(test_spec))

        status = subprocess.call(['python', '-m', 'pytest', '--verbose', test_spec])
    except:
        raise
    finally:
        print('[test_frontend] Terminating supervisord...')
        web_client.terminate()
        delete_test_yaml()

    sys.exit(status)
