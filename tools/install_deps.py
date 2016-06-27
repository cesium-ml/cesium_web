#!/usr/bin/env python

import sys
import re
import subprocess


if len(sys.argv) != 2:
    print("Usage: install_deps.py requirements.dev.txt")
    sys.exit(1)

req_file = sys.argv[1]

with open(req_file) as f:
    for dep in f:
        if not dep.strip():
            continue

        dep = re.split('\W+', dep)[0]
        try:
            __import__(dep.lower())
        except ImportError:
            print(("Development dependency '{}' unfulfilled. "
                   "Installing requirements.").format(dep))
            subprocess.call("pip install -r {}".format(req_file).split())
            break

print('Dependencies from {} verified.'.format(req_file))
