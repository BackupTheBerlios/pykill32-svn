"""Dump all modules loaded in a process.

$Id$

Usage:
dumpbin [-h] [pid]

if pid is not specified, the current process is used.
    
THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""


import sys
import os
from getopt import gnu_getopt as getopt, GetoptError

from toolhelp32 import FindModules



try:
    opts, args = getopt(sys.argv[1:], "h")
except GetoptError:
    sys.stdout.write(__doc__)
    sys.exit(2)


for o, a in opts:
    if o == "-h":
        sys.stdout.write(__doc__)
        sys.exit(0)


if len(args) > 0:
    pid = int(args[0])
else:
    pid = os.getpid()


for info in FindModules(pid):
    print "szModule:", info.szModule
    print "szExePath:", info.szExePath
    print "modBaseAddr:", info.modBaseAddr
    print "modBaseSize:", info.modBaseSize

    print
