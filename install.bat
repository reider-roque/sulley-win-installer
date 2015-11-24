@echo off

echo.
echo Make sure all 8 installation steps are run!
echo -------------------------------------------
echo.
pause

echo. && echo. && echo. && ^
echo 1. Installing Python 2.7... && ^
echo --------------------------- && ^
msiexec.exe /i python-2.7.10.msi /quiet /norestart && ^
echo. && echo. && echo. && ^
echo 2. Installing VC for Python 2.7... && ^
echo ---------------------------------- && ^
msiexec.exe /i VCForPython27.msi /quiet /norestart && ^
echo. && echo. && echo. && ^
echo 3. Adding Python to PATH... && ^
echo --------------------------- && ^
C:\Python27\python.exe pathvar.py -a C:\Python27 && ^
C:\Python27\python.exe pathvar.py -a C:\Python27\Scripts && ^
set path=%path%;C:\Python27\;C:\Python27\Scripts
echo. && echo. && echo. && ^
echo 4. Installing pydbg, pydasm and paimei... && ^
echo ----------------------------------------- && ^
cd pydbg-pydasm-paimei && ^
setup.py install && ^
cd .. && ^
echo. && echo. && echo. && ^
echo 5. Installing pcapy... && ^
echo ---------------------- && ^
set include=..\WpdPack\Include && ^
set lib=..\WpdPack\Lib && ^
cd pcapy && ^
C:\Python27\python.exe setup.py install && ^
cd .. && ^
echo. && echo. && echo. && ^
echo 6. Installing impacket... && ^
echo ------------------------- && ^
cd impacket && ^
C:\Python27\python.exe setup.py install && ^
cd .. && ^
echo. && echo. && echo. && ^
echo 7. Installing WinPcap... && ^
echo ------------------------ && ^
WinPcap_4_1_3.exe && ^
echo. && echo. && echo. && ^
echo 8. Installing uDraw(Graph)... && ^
echo ----------------------------- && ^
uDrawGraph-3.1.1-0-win32-en.exe && ^
echo. && echo. && echo. && ^
echo Installation is now complete! && ^
echo ----------------------------- && ^
pause && ^
echo. && echo. && echo. && ^
echo. && echo Thank you for flying Pythonic Airlines! && ^
echo.