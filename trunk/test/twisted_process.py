"""Test twisted process.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
Copyright (c) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

import os
import sys
import time

from win32api import GetProcAddress, GetModuleHandle

from twisted.internet import reactor, task


def shutdown():
    print "shutdown"
    fd.write("shutdown\n")

def timeout():
    print "timeout"
    fd.write("timeout\n")
    
    reactor.stop()


print "twisted process started, pid:", os.getpid()

if len(sys.argv) > 1:
    delay = int(sys.argv[1])
else:
    delay = 3

reactor.callLater(delay, timeout)
reactor.addSystemEventTrigger("before", "shutdown", shutdown)

# just use a file to comunicate
fd = file(".out", "w")

reactor.run()
