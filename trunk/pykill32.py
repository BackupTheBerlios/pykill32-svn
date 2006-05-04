"""pykill32: send signals to a remote (Python) process.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.

XXX TODO
"""

from win32api import GetProcAddress, GetModuleHandle, OpenProcess
from win32event import WaitForSingleObject, INFINITE 
from win32con import PROCESS_CREATE_THREAD, PROCESS_VM_OPERATION, \
    PROCESS_VM_WRITE


# unfortunately CreateRemoteThreas is not supplied with pywin32
def CreateRemoteThread(hProcess, pfn, param):
    from ctypes import windll, c_uint, c_void_p
    
    _CreateRemoteThread = windll.kernel32.CreateRemoteThread
    hProcess = c_uint(hProcess.handle) # XXX
    param = c_void_p(param)
    pfn = c_void_p(pfn) # XXX

    return _CreateRemoteThread(hProcess, c_void_p(), pfn, param, c_uint(0), c_void_p())



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
    flags = PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE
    hProcess = OpenProcess(flags, False, pid)

    # obtain the address of the raise method in the MSVCR71 module
    # XXX here we obtain the map address in the current address space,
    # just hope that the system map the CRT DLL at the same address
    # for every process.
    hModule = GetModuleHandle("MSVCR71");
    pfn = GetProcAddress(hModule, "raise");
  
    # create a remote thread that calls raise
    hThread = CreateRemoteThread(hProcess, pfn, sig)

    # wait for thread termination 
    WaitForSingleObject(hThread, INFINITE)


if __name__ == "__main__":
    import sys


    pid = int(sys.argv[1])
    signame = sys.argv[2]

    try:
        sig = signals[signame]
    except KeyError:
        print "invalid signal", sig
    else:
        kill(pid, sig)
