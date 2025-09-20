@echo off
echo Lenovo Laptop Sensor Monitor - Installation Script
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...

REM Install required packages
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully.
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
set "desktop=%USERPROFILE%\Desktop"
set "script_path=%~dp0lenovo_sensor_monitor.py"
set "shortcut_path=%desktop%\Lenovo Sensor Monitor.lnk"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut_path%'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%script_path%\"'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Lenovo Laptop Sensor Monitor'; $Shortcut.Save()}"

if exist "%shortcut_path%" (
    echo Desktop shortcut created successfully.
) else (
    echo Warning: Could not create desktop shortcut.
)

echo.
echo Installation completed!
echo.
echo You can now run the application by:
echo 1. Double-clicking the desktop shortcut
echo 2. Running: python lenovo_sensor_monitor.py
echo 3. Running: python -m lenovo_sensor_monitor
echo.

REM Ask if user wants to install as Windows service
set /p install_service="Do you want to install as a Windows service? (y/n): "
if /i "%install_service%"=="y" (
    echo Installing Windows service...
    python windows_service.py install
    if errorlevel 1 (
        echo Error: Failed to install Windows service
    ) else (
        echo Windows service installed successfully.
        echo You can start it with: python windows_service.py start
    )
)

echo.
echo Installation complete!
pause