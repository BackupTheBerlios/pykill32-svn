"""pykill32: send signals to a remote (Python) process.

Twisted process test.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""


import os
import time

from win32api import GetProcAddress, GetModuleHandle

from twisted.internet import reactor, task


i = 0
def timer():
    global i

    i += 1
    print i

def exit():
    print "exiting"


print "pid:", os.getpid()

mod = GetModuleHandle("MSVCR71")
print "proc address:", GetProcAddress(mod, "raise")

timerID = task.LoopingCall(timer)
timerID.start(1, False)

reactor.addSystemEventTrigger("before", "shutdown", exit)
reactor.run()
