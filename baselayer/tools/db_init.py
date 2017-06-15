#!/usr/bin/env python

import subprocess
import sys
import glob
import os
from baselayer.app.config import load_config


parent_yaml_files = glob.glob('../../*.yaml*') + glob.glob('*.yaml*')

parent_yaml_files = ([os.path.abspath(path) for path in parent_yaml_files] if
                     parent_yaml_files else None)


cfg = load_config(parent_yaml_files)

p = subprocess.run(['./baselayer/tools/db_init.sh', cfg['database:database'],
                    cfg['database:user']],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if p.returncode != 0:
    print('stdout:', p.stdout)
    print('stderr:', p.stderr)
    sys.exit(p.returncode)
