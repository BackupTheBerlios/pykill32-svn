"""pykill32: send signals to a remote (Python) process.

Test suite

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

import sys
import os
import time
import signal
import unittest

sys.path.append('../')

import win32api, pywintypes
import pykill32


class TestKill32(unittest.TestCase):
    """Test case for pykill32.
    """
    
    def setUp(self):
        self.bin = os.path.join(sys.prefix, "pythonw.exe")
        
    def testProcAddress(self):
        """Test that system maps 'raise' procedure of 'MSVCR71' module
        at the same address for all python processes.

        XXX This test should be more complete, as an example test if
        the address is the same for process under a different user
        account.
        """
        
        # get the address in our address space
        mod = win32api.GetModuleHandle("MSVCR71")
        address = win32api.GetProcAddress(mod, "raise")
        
#         command = """import win32api
#             mod = win32api.GetModuleHandle('MSVCR71')
#             print win32api.GetProcAddress(mod, 'raise')
#             """
        
        # run several python processes
        for i in range(10):
            stdin, stdout = os.popen4("python -")
            stdin.write("import win32api\n")
            stdin.write("mod = win32api.GetModuleHandle('MSVCR71')\n")
            stdin.write("print win32api.GetProcAddress(mod, 'raise')\n")
#            stdin.write(command)
            stdin.close()
            remoteAddress = int(stdout.read())

            self.failUnlessEqual(address, remoteAddress)

    def testProcessId(self):
        handle = os.spawnv(os.P_NOWAIT, self.bin, 
                          ["-c import time; time.sleep(3)"])
        pid = pykill32.GetProcessId(handle)
        self.failUnless(pid)

        self.failUnlessRaises(pywintypes.error, 
                              pykill32.GetProcessId,
                              0)
                          
    def testKillTERM(self):
        """Test of a clean shutdown of a Twisted process.
        """

        handle = os.spawnv(os.P_NOWAIT, self.bin,
                           [self.bin, "twisted_process.py"])

        time.sleep(1) # XXX give time to reactor to start
        pid = pykill32.GetProcessId(handle)
        pykill32.kill(pid, signal.SIGTERM)

        os.waitpid(handle, os.P_WAIT)
        lines = file(".out").readlines()

        self.failUnless("shutdown\n" in lines)
        self.failIf("timeout\n" in lines)

    def testKillILL(self):
        """Test of a forced shutdown od a Twisted process.
        """

        handle = os.spawnv(os.P_NOWAIT, self.bin, 
                           [self.bin, "twisted_process.py"])

        time.sleep(1)  # XXX give time to reactor to start
        pid = pykill32.GetProcessId(handle)
        pykill32.kill(pid, signal.SIGILL)

        os.waitpid(handle, os.P_WAIT)
        lines = file(".out").readlines()

        self.failIf("shutdown\n" in lines)
        self.failIf("timeout\n" in lines)

    
if __name__ == '__main__':
    unittest.main()

