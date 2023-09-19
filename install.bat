@echo off
setlocal

:: Check for Python installation
where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.x and rerun this script.
    pause
    goto :eof
)

:: Check Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %PYTHON_VERSION% | findstr /R "Python 3\..*" >nul
if errorlevel 1 (
    echo This script requires Python 3.x. Please install the correct version and rerun this script.
    pause
    goto :eof
)

:: Stop the Owlette Windows service if it's running
echo Stopping the Owlette Windows service if it's running...
net stop OwletteService

:: Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
cd %~dp0
python -m pip install -r requirements.txt

:: Install and start the Windows service
echo Installing and starting the Owlette Windows service...
cd %~dp0
cd src
python owlette_service.py install

:: Set the service to start automatically
sc config OwletteService start= delayed-auto

:: Start the service
python owlette_service.py start

:: Done
echo Installation complete!
endlocal

pause
