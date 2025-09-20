@echo off
echo Lenovo Laptop Sensor Monitor - Uninstallation Script
echo =====================================================

REM Stop and uninstall Windows service if installed
echo Checking for Windows service...
python windows_service.py stop >nul 2>&1
python windows_service.py uninstall >nul 2>&1

REM Remove desktop shortcut
echo Removing desktop shortcut...
set "desktop=%USERPROFILE%\Desktop"
set "shortcut_path=%desktop%\Lenovo Sensor Monitor.lnk"
if exist "%shortcut_path%" (
    del "%shortcut_path%"
    echo Desktop shortcut removed.
) else (
    echo No desktop shortcut found.
)

REM Ask if user wants to remove configuration files
set /p remove_config="Do you want to remove configuration files? (y/n): "
if /i "%remove_config%"=="y" (
    echo Removing configuration files...
    if exist "config.json" del "config.json"
    if exist "settings.json" del "settings.json"
    if exist "sensor_monitor.log" del "sensor_monitor.log"
    if exist "lenovo_sensor_service.log" del "lenovo_sensor_service.log"
    echo Configuration files removed.
)

REM Ask if user wants to uninstall Python packages
set /p remove_packages="Do you want to uninstall Python packages? (y/n): "
if /i "%remove_packages%"=="y" (
    echo Uninstalling Python packages...
    pip uninstall -y psutil WMI pywin32
    echo Python packages uninstalled.
)

echo.
echo Uninstallation completed!
echo.
echo Note: The application files are still in the installation directory.
echo You can delete the entire directory if you no longer need the application.
echo.
pause