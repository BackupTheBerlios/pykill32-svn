"""pykill32: send signals to a remote (Python) process.

Test script for the C implementation.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

import sys
import os
import time
from signal import SIGTERM

from win32api import GetProcAddress, GetModuleHandle

from cpykill32 import kill
from pykill32 import signals 


mod = GetModuleHandle("MSVCR71")
print "proc address:", GetProcAddress(mod, "raise")

if len(sys.argv) > 2:
    pid = int(sys.argv[1])
    sig = signals[sys.argv[2]]
    
    kill(pid, sig)
else:
    pid = os.getpid()
    print "pid:", pid
    kill(pid, SIGTERM)
    time.sleep(50)

