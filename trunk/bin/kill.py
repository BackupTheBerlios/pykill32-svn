"""Command line interface for kill32, 
with emulation of POSIX kill(1).

$Id$

kill [-l] [-s] pid
    
s can be a number or a string.
l list all supported signals.
    
If no signal is specified, the TERM signal is sent.

THIS SOFTWARE IS UNDER MIT LICENSE.
Copyright (c) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""
    
import sys
import signal
from getopt import gnu_getopt as getopt, GetoptError

from kill32 import signals, kill
    
try:
    opts, args = getopt(sys.argv[1:], "hls:")
except GetoptError:
    sys.stdout.write(__doc__)
    sys.exit(2)

    
sig = None
for o, a in opts:
    if o == "-l":
        print '\n'.join(signals.keys())
        sys.exit(0)
    if o == "-h":
        sys.stdout.write(__doc__)
        sys.exit(0)
    elif o == "-s":
        sig = a
    # XXX TODO -t

if len(args) == 0:
    sys.stdout.write(__doc__)
    sys.exit(2) 
    
try:
    pid = int(args[0])
except ValueError:
    print "invalid pid"
    sys.exit(2)

    
if sig is None:
    sig = signal.SIGTERM
else:
    if sig.isdigit():
        sig = int(sig)
    else:
        try:
            sig = signals[sig]
        except KeyError:
            print "invalid signal", sig


kill(pid, sig)

    
