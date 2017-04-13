#!/usr/bin/env python
import sys
import subprocess

if len(sys.argv) != 2:
    print("Usage: install_deps.py requirements.dev.txt")
    sys.exit(1)

req_file = sys.argv[1]

subprocess.call("pip install setuptools".split())
from pkg_resources import require, DistributionNotFound, VersionConflict

with open(req_file) as f:
    deps = f.read()
    try:
        require(deps)
    except (DistributionNotFound, VersionConflict) as e:
        print(("Development dependency '{}' unfulfilled. "
               "Installing requirements.").format(e.req.project_name))
        p = subprocess.call("pip install -r {}".format(req_file).split())
        sys.exit(p)

print('Dependencies from {} verified.'.format(req_file))
