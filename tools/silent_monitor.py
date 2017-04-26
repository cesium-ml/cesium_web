#!/usr/bin/env python

import subprocess
import sys
import shlex

if len(sys.argv) < 2:
    print('Usage: silent_monitor.py <cmd to execute>')
    sys.exit()

cmd = ' '.join(sys.argv[1:])

tag = 'Silently executing: {}'.format(cmd)
print('[·] {}'.format(tag), end='')
sys.stdout.flush()

p = subprocess.Popen(shlex.split(cmd),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

err = p.wait()
stdout, stderr = p.stderr.read().strip(), p.stdout.read().strip()

if err == 0:
    print('\r[✓] {}'.format(tag))
else:
    print('\r[✗] {}'.format(tag))
    print('\n! Failure (exit code {}).'.format(err, cmd))

    if stdout:
        print('--- stdout ---')
        print(stdout.decode('utf-8'))

    if stderr:
        print('--- stderr ---')
        print(stderr.decode('utf-8'))

    if stdout or stderr:
        print('--- end ---')

    sys.exit(err)
