/*
  Send signals to a remote (Python) process.

  $Id$

  THIS SOFTWARE IS UNDER MIT LICENSE.
  (C) 2006 Perillo Manlio (manlio.perillo@gmail.com)
  
  Read LICENSE file for more informations.
*/


#include <windows.h>
#include <python.h>


static PyObject *
kill(PyObject *self, PyObject *args)
{
  /* TODO: returns Windows errors */
  
  unsigned long pid;
  int sig;
  
  HANDLE hProcess = NULL;
  HANDLE hThread = NULL;
  HANDLE hModule = NULL;
  
  int flags;
  PTHREAD_START_ROUTINE pf;
  
  if (!PyArg_ParseTuple(args, "ki", &pid, &sig))
    return NULL;
  
  /* open the remote process */
  flags = PROCESS_CREATE_THREAD | PROCESS_VM_OPERATION | PROCESS_VM_WRITE;
  hProcess = OpenProcess(flags, FALSE, pid);
  
  if (!hProcess) {
    PyErr_SetString(PyExc_OSError, "unable to open remote process");
    goto cleanup;
  }
  
  /* 
     obtain the address of the raise method in the MSVCR71 module.
     XXX here we obtain the map address in the current address space,
     just hope that the system map the CRT DLL at the same address for
     every process.
  */
  hModule = GetModuleHandle("MSVCR71");
  pf = (PTHREAD_START_ROUTINE) GetProcAddress(hModule, "raise");

  if (!pf) {
    PyErr_SetString(PyExc_OSError, "unable to retrieve procedure address");
    goto cleanup;
  }
  
  /* create a remote thread that calls the raise function */
  hThread = CreateRemoteThread(hProcess, NULL, 0, pf, (void*)sig, 0, NULL);

  if (!hThread) {
    PyErr_SetString(PyExc_OSError, "unable to start remote thread");
    goto cleanup;
  }

  /* wait for thread termination */
  WaitForSingleObject(hThread, INFINITE);


 cleanup:
  if (hThread)
    CloseHandle(hThread);

  if (hProcess)
    CloseHandle(hProcess);

  Py_RETURN_NONE;
}


static PyMethodDef pykill32Methods[] = {
  {"kill", kill, METH_VARARGS,
   "Send a signal to a remote (Python) process."},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC
initcpykill32(void)
{
  Py_InitModule("cpykill32", pykill32Methods);
}
