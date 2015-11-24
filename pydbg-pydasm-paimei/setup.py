#!c:\python\python.exe

# $Id: setup.py 238 2010-04-05 20:40:46Z rgovostes $

import os.path as path
import shutil
import sys

from distutils.core import setup
from distutils.util import get_platform

# Determine the target platform
pydasm_platform = "{}-{}.{}".format(
    get_platform(),
    sys.version_info[0], 
    sys.version_info[1]
)

# Copy the correct version of precompiled binary into pydbg package root
pydasm_src = path.join("pydasm", pydasm_platform, "pydasm.pyd")
pydasm_dst = path.join("pydasm", "pydasm.pyd")
shutil.copyfile(pydasm_src, pydasm_dst)

setup( 
       name         = "PaiMei",
       version      = "1.2",
       description  = "PaiMei - Reverse Engineering Framework",
       author       = "Pedram Amini",
       author_email = "pedram.amini@gmail.com",
       url          = "http://www.openrce.org",
       license      = "GPL",
       packages     = ["pida", "pgraph", "pydbg", "utils", "pydasm"],
       package_data = { 
                         "pydasm": ["pydasm.pyd"]
                      }
)