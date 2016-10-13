#!/usr/bin/env python

import sys
import re
import subprocess


pkg_import = {'pyyaml': 'yaml',
              'pyzmq': 'zmq',
              'pyjwt': 'jwt'}


if len(sys.argv) != 2:
    print("Usage: install_deps.py requirements.dev.txt")
    sys.exit(1)

req_file = sys.argv[1]

with open(req_file) as f:
    for dep in f:
        dep = dep.strip()
        if not dep:
            continue

        if '-e' in dep:
            dep = dep.split('#egg=')[-1]   # use the egg name
        else:
            dep = re.split('\W+', dep)[0]  # discard version info

        try:
            __import__(pkg_import.get(dep, dep))
        except ImportError:
            print(("Development dependency '{}' unfulfilled. "
                   "Installing requirements.").format(dep))
            subprocess.call("pip install -r {}".format(req_file).split())
            sys.exit(0)

print('Dependencies from {} verified.'.format(req_file))
