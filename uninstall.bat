@echo off
setlocal

:: Check for Python installation
where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Cannot proceed with uninstallation.
    goto :eof
)

:: Check Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %PYTHON_VERSION% | findstr /R "Python 3\..*" >nul
if errorlevel 1 (
    echo This script requires Python 3.x. Cannot proceed with uninstallation.
    goto :eof
)

:: Stop the Owlette Windows service if it's running
echo Stopping the Owlette Windows service if it's running...
net stop OwletteService

:: Uninstall the Owlette Windows service
echo Uninstalling the Owlette Windows service...
cd %~dp0
cd src
python owlette_service.py remove

:: Optional: Ask the user if they want to remove Python dependencies
set /p uninstall_deps=Do you want to remove Python dependencies? (y/n):
if "%uninstall_deps%"=="y" (
    echo Uninstalling Python dependencies...
    cd %~dp0
    python -m pip uninstall -r requirements.txt -y
) else if "%uninstall_deps%"=="n" (
    echo Skipping Python dependency removal.
) else (
    echo Invalid choice. Skipping Python dependency removal.
)

:: Done
echo Uninstallation complete!
endlocal

pause
