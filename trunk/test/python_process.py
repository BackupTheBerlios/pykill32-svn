"""Test twisted process.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
Copyright (c) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

import os
import sys
import time
import signal
import atexit
import thread

from win32api import GetProcAddress, GetModuleHandle



def handler(signum, frame):
    print "signal handler, tid:", thread.get_ident()
    fd.write("signal handler\n")
    

def shutdown():
    print "atexit"
    fd.write("atexit\n")
    


print "python process started, pid: %d, tid: %d" % (os.getpid(), 
                                                   thread.get_ident())

if len(sys.argv) > 1:
    delay = int(sys.argv[1])
else:
    delay = 3


atexit.register(shutdown)
signal.signal(signal.SIGTERM, handler)

# just use a file to comunicate
fd = file(".out", "w")

time.sleep(delay)

