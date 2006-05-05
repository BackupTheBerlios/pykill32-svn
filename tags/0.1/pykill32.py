"""pykill32: send signals to a remote (Python) process.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

from win32api import GetProcAddress, GetModuleHandle, OpenProcess
from win32event import WaitForSingleObject, INFINITE 
from win32con import PROCESS_CREATE_THREAD, PROCESS_VM_OPERATION



# CreateRemoteThreas is not supplied with pywin32
def CreateRemoteThread(hProcess, pfn, param):
    from win32api import GetLastError, FormatMessage
    from pywintypes import error, HANDLE
    from ctypes import windll, c_uint, c_void_p
    
    
    _CreateRemoteThread = windll.kernel32.CreateRemoteThread
    hProcess = c_uint(hProcess.handle) # XXX
    param = c_void_p(param)
    pfn = c_void_p(pfn) # XXX

    hThread = _CreateRemoteThread(hProcess, c_void_p(), c_uint(0),
                                  pfn, param, c_uint(0), c_void_p())

    if not hThread:
        err = GetLastError()
        errmsg = FormatMessage(err)
        raise error(err, "CreateRemoteThread", errmsg)

    return HANDLE(hThread)


def GetRemoteProcAddress(hProcess, module, proc):
    """Get the base address, in the remote address space, at which
    the procedure of the given module is mapped.

    XXX in the current implementation we just get the base address in
    *our* address space. This suppose:
    - the remote process include the given module
    - the system maps the module at the same address for every process

    This just works for MSVCR71 for Python processes;
    if this is not the case (*no* check are done) the remote process
    degrade to undefined behavior.
    
    XXX TODO implement this function in the right way,
             rename to GetProvAddressEx?
    """

    handle = GetModuleHandle(module)
    return GetProcAddress(handle, proc)


# XXX this is not supplied with pywin32, added here because os.spawn
# returns process handle
def GetProcessId(handle):
    """Get the process id, given the process handle.
    """

    from win32api import GetLastError, FormatMessage
    from pywintypes import error, HANDLE
    from ctypes import windll, c_uint
    
    handle = c_uint(handle)
    _GetProcessId = windll.kernel32.GetProcessId
    pid = _GetProcessId(handle)

    if not pid:
        err = GetLastError()
        errmsg = FormatMessage(err)
        raise error(err, "GetProcessId", errmsg)

    return pid
    

# supported signals under Windows    
signals = {
    "ABRT": 22, 
    "BREAK": 21,
    "FPE": 8,
    "ILL": 4,
    "INT": 2,
    "SEGV": 11,
    "TERM": 15,
    }


def kill(pid, sig):
    """Send the signal sig to the remote process.
    """
  
    # open the remote process
    # XXX why do we need PROCESS_VM_OPERATION?
    flags = PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION
    hProcess = OpenProcess(flags, False, pid)

    # obtain the address of the raise method in the MSVCR71 module
    pfn = GetRemoteProcAddress(pid, "MSVCR71", "raise")
  
    # create a remote thread that calls raise
    hThread = CreateRemoteThread(hProcess, pfn, sig)

    # wait for thread termination 
    WaitForSingleObject(hThread, INFINITE)


def main():
    """Command line interface for pykill32, 
with emulation of POSIX kill(1).

kill [-l] [-s] pid
    
s can be a number or a string.
l list all supported signals.
    
If no signal is specified, the TERM signal is sent.

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
    """
    
    import sys
    import signal
    from getopt import gnu_getopt as getopt, GetoptError

    
    try:
        opts, args = getopt(sys.argv[1:], "hls:")
    except GetoptError:
        sys.stdout.write(main.__doc__)
        sys.exit(2)

    
    sig = None
    for o, a in opts:
        if o == "-l":
            print ', '.join(signals.keys())
            sys.exit(0)
        if o == "-h":
            sys.stdout.write(main.__doc__)
            sys.exit(0)
        elif o == "-s":
            sig = a

    if len(args) == 0:
        sys.stdout.write(main.__doc__)
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

    
if __name__ == "__main__":
    main()
