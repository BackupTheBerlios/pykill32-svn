"""pykill32: send signals to a remote (Python) process.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

from win32api import GetProcAddress, GetModuleHandle, OpenProcess
from win32event import WaitForSingleObject, INFINITE 
from win32con import PROCESS_CREATE_THREAD, PROCESS_VM_OPERATION

# unfortunately CreateRemoteThreas is not supplied with pywin32
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


signals = {
    "SIGABRT": 22, 
    "SIGBREAK": 21,
    "SIGFPE": 8,
    "SIGILL": 4,
    "SIGINT": 2,
    "SIGSEGV": 11,
    "SIGTERM": 15,
    }

def kill(pid, sig):
    """Send the signal sig to the remote process.
    """
  
    # open the remote process
    # XXX why we need PROCESS_VM_OPERATION?
    flags = PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION
    hProcess = OpenProcess(flags, False, pid)

    # obtain the address of the raise method in the MSVCR71 module
    # XXX here we obtain the map address in the current address space,
    # just hope that the system map the CRT DLL at the same address
    # for every process.
    hModule = GetModuleHandle("MSVCR71") # XXX is this the lib to use?
    pfn = GetProcAddress(hModule, "raise")
  
    # create a remote thread that calls raise
    hThread = CreateRemoteThread(hProcess, pfn, sig)

    # wait for thread termination 
    WaitForSingleObject(hThread, INFINITE)


def main():
    """Command line interface for pykill32.
    """
    
    import sys


    pid = int(sys.argv[1])
    signame = sys.argv[2]

    try:
        sig = signals[signame]
    except KeyError:
        print "invalid signal", sig
    else:
        kill(pid, sig)

if __name__ == "__main__":
    main()
