"""Test suite for kill32 module.

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
import toolhelp32
import kill32


class TestKill32(unittest.TestCase):
    """Test case for pykill32.
    """
    
    def setUp(self):
        self.bin = os.path.join(sys.prefix, "python.exe")
    

    def testProcAddress(self):
        """Test that system maps 'raise' procedure of 'MSVCR71' module
        at the same address for all python processes.

        XXX This test should be more complete, as an example test if
        the address is the same for process under a different user
        account.
        """
        
        # get the address in our address space
        mod = win32api.GetModuleHandle("MSVCR71.dll")
        address = win32api.GetProcAddress(mod, "raise")
        
        cmd = "import win32api; " \
            "mod = win32api.GetModuleHandle('MSVCR71.dll'); " \
            "print win32api.GetProcAddress(mod, 'raise')"

        # run several python processes
        for i in range(10):
            stdin, stdout = os.popen4("python -u -")
            stdin.write(cmd)
            stdin.close()
            remoteAddress = int(stdout.read())

            self.failUnlessEqual(address, remoteAddress)

    def testKillTERMTwisted(self):
        """Test of a clean shutdown of a Twisted process.
        """

        handle = os.spawnv(os.P_NOWAIT, self.bin,
                           [self.bin, "twisted_process.py"])

        time.sleep(1) # XXX give time to reactor to start
        pid = toolhelp32.GetProcessId(handle)
        kill32.kill(pid, signal.SIGTERM)

        os.waitpid(handle, os.P_WAIT)
        lines = file(".out").readlines()

        self.failUnless("shutdown\n" in lines)
        self.failIf("timeout\n" in lines)

        os.remove(".out")

    def testKillTERMPython(self):
        """Test of a clean shutdown of a Python process.
        """

        handle = os.spawnv(os.P_NOWAIT, self.bin,
                           [self.bin, "python_process.py"])

        time.sleep(1) # XXX give time to process to start
        pid = toolhelp32.GetProcessId(handle)
        kill32.kill(pid, signal.SIGTERM)

        os.waitpid(handle, os.P_WAIT)
        lines = file(".out").readlines()

        self.failUnless("signal handler\n" in lines)
        self.failUnless("atexit\n" in lines)

        os.remove(".out")

    def testKillILL(self):
        """Test of a forced shutdown od a Twisted process.
        """

        handle = os.spawnv(os.P_NOWAIT, self.bin, 
                           [self.bin, "twisted_process.py"])

        time.sleep(1)  # XXX give time to reactor to start
        pid = toolhelp32.GetProcessId(handle)
        kill32.kill(pid, signal.SIGILL)

        os.waitpid(handle, os.P_WAIT)
        lines = file(".out").readlines()

        self.failIf("shutdown\n" in lines)
        self.failIf("timeout\n" in lines)
        
        os.remove(".out")


if __name__ == '__main__':
    unittest.main()

