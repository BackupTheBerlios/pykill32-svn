"""pykill32: send signals to a remote (Python) process.

Setup script

$Id$

THIS SOFTWARE IS UNDER MIT LICENSE.
(C) 2006 Perillo Manlio (manlio.perillo@gmail.com)

Read LICENSE file for more informations.
"""


from distutils.core import setup, Extension


#pykill32 = Extension("cpykill32", ["cpykill32.c"], libraries=["Kernel32"])
            
setup(name="pykill32",
      version="0.2",
      author="Manlio Perillo",
      author_email="manlio.perillo@gmail.com",
      description="send signals to a remote (Python) process",
      license="MIT",
      url="http://developer.berlios.de/projects/pykill32/",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "License :: OSI Approved :: MIT License",
          # XXX only for Windows 2000 and superior
          "Operating System :: Microsoft :: Windows :: Windows NT/2000", 
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      py_modules = ["kill32", "toolhelp32"], # ext_modules=[cpykill32]
      scripts = ["bin/kill.py", "bin/dumpbin.py"]
      )
