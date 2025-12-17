@echo off
echo ================================================
echo Robot Hand Controller - Quick Start
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python detected: 
python --version
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show mediapipe >nul 2>&1
if errorlevel 1 (
    echo.
    echo MediaPipe not found. Installing dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed!
)

echo.
echo ================================================
echo Choose an option:
echo ================================================
echo.
echo 1. List available COM ports
echo 2. Run robot controller
echo 3. Run web interface (local network)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto listports
if "%choice%"=="2" goto runcontroller
if "%choice%"=="3" goto runweb
if "%choice%"=="4" goto end

echo Invalid choice!
pause
exit /b 1

:listports
echo.
echo ================================================
echo Available Serial Ports:
echo ================================================
python local_client.py --list-ports
echo.
pause
goto end

:runcontroller
echo.
set /p port="Enter COM port (e.g., COM14): "
if "%port%"=="" (
    echo ERROR: No port specified!
    pause
    goto end
)

echo.
echo Do you want to enable serial communication?
set /p enableserial="Enable serial? (y/n): "

set serialflag=
if /i "%enableserial%"=="y" set serialflag=--enable-serial

echo.
echo Starting robot controller...
echo Press ESC in the video window to stop
echo.
python local_client.py --serial-port %port% %serialflag%
pause
goto end

:runweb
echo.
echo Starting web interface...
echo Access from other devices at: http://YOUR-IP:8501
echo Press Ctrl+C to stop
echo.
streamlit run streamlit_app.py --server.address 0.0.0.0
pause
goto end

:end
echo.
echo Goodbye!
