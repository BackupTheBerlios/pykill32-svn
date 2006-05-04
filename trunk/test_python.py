"""pykill32: send signals to a remote (Python) process.

Python process test.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""


import os
import time
import atexit

from win32api import GetProcAddress, GetModuleHandle

def exit():
    print "exiting"


atexit.register(exit)

print "pid:", os.getpid()

mod = GetModuleHandle("MSVCR71")
print "proc address:", GetProcAddress(mod, "raise")

time.sleep(100)


