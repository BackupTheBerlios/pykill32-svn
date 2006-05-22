"""toolhelp32: interface to ToolHelp32 functions

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
Copyright (c) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

from win32api import GetLastError, FormatMessage
from pywintypes import error, HANDLE

from ctypes import windll, Structure, sizeof, pointer
from ctypes import c_char, c_int, c_uint, c_void_p, c_char_p



def _error(routine):
    # internal helper
    err = GetLastError()
    errmsg = FormatMessage(err)
    raise error(err, routine, errmsg)

_kernel = windll.kernel32



TH32CS_SNAPMODULE = 8
MAX_MODULE_NAME32 = 255
MAX_PATH = 260


class MODULEENTRY32(Structure):
    _fields_ = [
        ("dwSize", c_uint),
        ("th32ModuleID", c_uint),
        ("th32ProcessID", c_uint),
        ("GlblcntUsage", c_uint),
        ("ProccntUsage", c_uint),
        ("modBaseAddr", c_void_p), # XXX c_char_p
        ("modBaseSize", c_uint),
        ("hModule", c_uint),
        ("szModule", c_char * (MAX_MODULE_NAME32 + 1)),
        ("szExePath", c_char * MAX_PATH)
        ]

    def __init__(self):
        self.dwSize = sizeof(MODULEENTRY32)


# this seems to be not supplied with pywin32
def GetProcessId(handle):
    """Get the process id, given the process handle.
    """

    _GetProcessId = _kernel.GetProcessId
    
    pid = _GetProcessId(c_uint(handle))

    if not pid:
        _error("GetProcessId")

    return int(pid)


def CreateRemoteThread(hProcess, pfn, param):
    """Create a remote thread in the given process.

    param will be passed to the function.
    
    Note that the function address must be in the remote process
    address space.
    """
    
    _CreateRemoteThread = _kernel.CreateRemoteThread
    
    hProcess = c_uint(hProcess)
    param = c_void_p(param)
    pfn = c_void_p(pfn) # XXX

    hThread = _CreateRemoteThread(hProcess, c_void_p(), c_uint(0),
                                  pfn, param, c_uint(0), c_void_p())
    
    if not hThread:
        _error("CreateRemoteThread")

    return HANDLE(hThread)


def CreateToolhelp32Snapshot(flags, pid):
    """Create a snapshot with ToolHelp.
    """
    
    _CreateToolhelp32Snapshot = _kernel.CreateToolhelp32Snapshot

    handle = _CreateToolhelp32Snapshot(c_uint(flags), c_uint(pid))
    
    if handle == -1:
        _error("CreateToolhelp32Snapshot")

    return HANDLE(handle)


def FindModules(pid):
    """High level interface to Module32First/Next.

    Return an iterator with all info about loaded modules in the given
    process.
    """

    Module32First = _kernel.Module32First
    Module32Next = _kernel.Module32Next

    
    hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
    handle = hSnapshot.handle
    info = MODULEENTRY32()
    
    if not Module32First(c_uint(handle), pointer(info)):
        _error("Module32First")

    while True:
        yield info
        
        if not Module32Next(c_uint(handle), pointer(info)):
            break
