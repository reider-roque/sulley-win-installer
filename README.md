# Description

Sulley Framework Windows semi-automatic offline installer with all dependencies. Semi-automatic means that you will have to click-through the WinPcap and uDrawGraph GUI installers. Otherwise everything is installed without user interaction.

# Contents

pcapy, impacket, and sulley are master branches pulled off GitHub on or around Nov 20 2015.

pydbg-pydasm-paimei package was pulled from my repository I created earlier.

Python version 2.7.10.

VCForPython27 installs Microsoft C/C++ compiler and linker to satisfy pcapy installation time dependency.

WpdPack directory contains WinPcap Developer's Kit version 4.1.2, pcapy installation time dependency.

WinPcap version 4.1.3 is pcapy dependency.

uDrawGraph is needed to open .udg graphs produced by sulley\utils\crashbin_explorer.py with -g flag.

pathvar.py is a script that adds C:\Python27 and C:\Python27\Scripts directories to system PATH.

install.bat is a script that pulls everything together into one nice installer.