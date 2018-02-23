# Derived from `distributed.diagnostics.progressbar` which is

# Copyright (c) 2015-2017, Anaconda, Inc. and contributors
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# Neither the name of Anaconda nor the names of any contributors may
# be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


from distributed.diagnostics.progressbar import ProgressBar
from tornado.ioloop import IOLoop

from contextlib import contextmanager
import sys


def format_time(t):
    "Format seconds into a human readable form."
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d}'


class WebSocketProgressBar(ProgressBar):
    def __init__(self, keys, update_callback, scheduler=None, interval=1,
                 loop=None, complete=True, start=True):
        super(WebSocketProgressBar, self).__init__(keys, scheduler, interval,
                                                   complete)
        self.update_callback = update_callback
        self.loop = loop or IOLoop.current()

        if start:
            self.loop.add_callback(self.listen)

    def _draw_bar(self, remaining, all, **kwargs):
        frac = (1 - remaining / all) if all else 1.0
        percent = frac * 100
        elapsed = format_time(self.elapsed)
        self.update_callback({'percent': f'{percent:2.1f}', 'elapsed': elapsed})
