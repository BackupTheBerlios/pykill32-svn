"""Test suite for toolhelp32 module.

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""

import sys
import os
import unittest

sys.path.append('../')

import pywintypes
import toolhelp32


class TestKill32(unittest.TestCase):
    """Test case for pykill32.
    """
    
    def setUp(self):
        self.bin = os.path.join(sys.prefix, "python.exe")
    

    def testProcessId(self):
        """Test the ProcessId function.
        """

        handle = os.spawnv(os.P_NOWAIT, self.bin, 
                          [self.bin, "-c", '"import time; time.sleep(3)"'])
        pid = toolhelp32.GetProcessId(handle)
        self.failUnless(pid)

        self.failUnlessRaises(pywintypes.error, 
                              toolhelp32.GetProcessId,
                              0)
                          
    
    def testFindModulesLocal(self):
        """Test the FindModules function, on local process.
        """

        pid = os.getpid()
        
        modules = [
            info.szModule 
            for info in toolhelp32.FindModules(pid)
            ]
        
        self.failUnless("msvcrt.dll" in modules)
        
        # XXX this is valid only for Python 2.4?
        if 1:
            self.failUnless("MSVCR71.dll" in modules)

    def testFindModules(self):
        """Test the FindModules function.

        XXX understand why this fails.
        """

        handle = os.spawnv(os.P_NOWAIT, self.bin, 
                          [self.bin, "-c", '"import time; time.sleep(3)"'])
        pid = toolhelp32.GetProcessId(handle)
        
        modules = [
            info.szModule 
            for info in toolhelp32.FindModules(pid)
            ]
        
        self.failUnless("msvcrt.dll" in modules)
        
        # XXX this is valid only for Python 2.4?
        if 1:
            self.failUnless("MSVCR71.dll" in modules)

    
if __name__ == '__main__':
    unittest.main()

