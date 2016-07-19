#!/usr/bin/env python

import sys
import json
import os
from os.path import join as pjoin
import subprocess


if len(sys.argv) != 2:
    print("Usage: install_npm_deps.py package.json")
    sys.exit(1)

pkg_file = sys.argv[1]

with open(pkg_file) as f:
    deps = json.load(f)
    all_deps = deps['dependencies']
    all_deps.update(deps['devDependencies'])

for dep in all_deps:
    pkg_path = pjoin(os.path.dirname(os.path.abspath(pkg_file)))
    if not os.path.exists(pjoin(pkg_path, 'node_modules', dep)):
        print(("Development dependency '{}' unfulfilled. "
               "Installing requirements.").format(dep))
        subprocess.call("npm install".split())
        sys.exit(0)

print('Dependencies from {} verified.'.format(pkg_file))
