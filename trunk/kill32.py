"""pykill32: send signals to a remote (Python) process.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
Copyright (c) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""


from win32api import GetProcAddress, GetModuleHandle, OpenProcess
from win32event import WaitForSingleObject, INFINITE 
from win32con import PROCESS_CREATE_THREAD, PROCESS_VM_OPERATION
from toolhelp32 import FindModules, CreateRemoteThread


def findCRTModules(pid):
    """Find all the C Runtime Library loaded in the process.

    Returna an iterator that returns a tuple with module 
    name, module version, address
    """
    
    # map every know CRT DLL
    libcVersions = {
        "msvcrt.dll": 1,
        "MSVCR71.dll": 7.1,
        "MSVCR80.dll": 8.0
        }
        
    
    for info in FindModules(pid):
        version = libcVersions.get(info.szModule, None)
        if version:
            yield info.szModule, version, info.modBaseAddr
        

def getSignalProcedure(pid):
    """Get the base address, in the remote address space, at which
    the 'raise' procedure of the C Runtime Library module is mapped.

    XXX in the current implementation we just get the base address in
    *our* address space. This suppose:
    - the remote process include the given module
    - the system maps the module at the same address for every process

    This just works for 'msvcrt.dll' and virtually every Windows program
    include this library. 
    
    XXX we first retrieve all the C Runtime modules loaded in the process
    and use the most recent version
    """

    libc = list(findCRTModules(pid))

    if not libc:
        raise OSError("C Runtime not found", pid)
    
    # use the most recent version
    libc.sort(lambda i, j: cmp(i[2], j[2]))
    module, version, baseAddress = libc[-1]

    # find the map address of the procedure in the local process
    handle = GetModuleHandle(module)
    address = GetProcAddress(handle, "raise")
    
    if baseAddress != handle:
        # the module is mapped at a different address
        # XXX TODO the offset of the procedure should be the same, so
        # it should be still possible to obtain the proc address
#        address = baseAddress + (address - handle)
        raise AssertionError("module address mismatch", module)
    
    return address


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

    # obtain the address of the raise method in the C Runtime module
    pfn = getSignalProcedure(pid)
  
    # create a remote thread that calls raise
    hThread = CreateRemoteThread(hProcess.handle, pfn, sig)

    # wait for thread termination 
    WaitForSingleObject(hThread, INFINITE)
