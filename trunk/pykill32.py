"""pykill32: send signals to a remote (Python) process.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

from win32api import GetProcAddress, GetModuleHandle, OpenProcess
from win32api import GetLastError, FormatMessage
from pywintypes import error, HANDLE
from win32event import WaitForSingleObject, INFINITE 
from win32con import PROCESS_CREATE_THREAD, PROCESS_VM_OPERATION

from ctypes import windll, Structure, sizeof, pointer
from ctypes import c_char, c_int, c_uint, c_void_p, c_char_p



def _error(routine):
    # internal helper
    err = GetLastError()
    errmsg = FormatMessage(err)
    raise error(err, routine, errmsg)


def GetProcessId(handle):
    """Get the process id, given the process handle.
    """

    _GetProcessId = windll.kernel32.GetProcessId
    
    handle = c_uint(handle)
    
    pid = _GetProcessId(handle)

    if not pid:
        _error("GetProcessId")

    return pid


def FindModule(pid, module):
    """Find the map address of the given module (DLL) in the given
    process.

    If the module is not found, returns None.

    XXX TODO return an iterator with all modules that match a pattern
    (multiple version of the same module)?
    """

    TH32CS_SNAPMODULE = 8
    MAX_MODULE_NAME32 = 255
    MAX_PATH = 260
    
    CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
    Module32First = windll.kernel32.Module32First
    Module32Next = windll.kernel32.Module32Next

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
        
    me32 = MODULEENTRY32()
    handle = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, c_int(pid))
    
    if handle == -1:
        _error("CreateToolhelp32Snapshot")

    me32.dwSize = sizeof(MODULEENTRY32) 
 
    if not Module32First(handle, pointer(me32)):
        _error("Module32First")

    while True:
        if me32.szModule == module:
            return me32.modBaseAddr
        
        if not Module32Next(handle, pointer(me32)):
            break

    return None


def GetRemoteProcAddress(pid, module, proc):
    """Get the base address, in the remote address space, at which
    the procedure of the given module is mapped.

    XXX in the current implementation we just get the base address in
    *our* address space. This suppose:
    - the remote process include the given module
    - the system maps the module at the same address for every process

    This just works for 'msvcrt.dll' and virtually every Windows program
    include this library. 
    
    A sanity check is done.

    XXX TODO rename to GetProcAddressEx?
    """

    # find the map address of the module in the remote process
    baseAddress = FindModule(pid, module)
    if baseAddress is None:
        raise AssertionError("module not found", module)
    
    # find the map address of the procedure in the local process
    handle = GetModuleHandle(module)
    address = GetProcAddress(handle, proc)
    
    if baseAddress != handle:
        # the module is mapped at a different address
        # XXX TODO the offset of the procedure should be the same, so
        # it should be still possible to obtain the proc address
#        address = baseAddress + (address - handle)
        raise AssertionError("module address mismatch", module)
    
    return address


def CreateRemoteThread(hProcess, pfn, param):
    """Create a remote thread in the given process.

    param will be passed to the function.
    
    Note that the function address must be in the remote process
    address space.
    """
    
    _CreateRemoteThread = windll.kernel32.CreateRemoteThread
    
    hProcess = c_uint(hProcess) # XXX
    param = c_void_p(param)
    pfn = c_void_p(pfn) # XXX

    hThread = _CreateRemoteThread(hProcess, c_void_p(), c_uint(0),
                                  pfn, param, c_uint(0), c_void_p())
    
    if not hThread:
        _error("CreateRemoteThread")

    return HANDLE(hThread)
    


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

    # XXX use the latest version of the C Runtime
    # XXX TODO: there is version 8, too
    if FindModule(pid, "MSVCR71.dll"):
        module = "MSVCR71.dll"
    else:
        module = "msvcrt.dll"
        
    # obtain the address of the raise method in the MSVCR71 module
    pfn = GetRemoteProcAddress(pid, module, "raise")
  
    # create a remote thread that calls raise
    hThread = CreateRemoteThread(hProcess.handle, pfn, sig)

    # wait for thread termination 
    WaitForSingleObject(hThread, INFINITE)
