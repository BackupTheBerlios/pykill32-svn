"""pykill32: send signals to a remote (Python) process.

Setup script

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""


from distutils.core import setup, Extension


cpykill32 = Extension('cpykill32', ['cpykill32.c'], libraries=['Kernel32'])
            
    
setup(name='pykill32',
      version='0.1',
      py_modules = ["pykill32"],
      ext_modules=[cpykill32]
      )
