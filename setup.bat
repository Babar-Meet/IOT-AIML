@echo off
setlocal EnableExtensions

pushd "%~dp0" >nul

title IOT-AIML - Setup
echo ============================================================
echo   IOT-AIML SYSTEM - SETUP
echo ============================================================
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    popd >nul
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
if exist "venv" (
    echo       Virtual environment already exists. Removing old one...
    rmdir /s /q "venv"
    if errorlevel 1 (
        echo [ERROR] Could not remove old virtual environment.
        popd >nul
        pause
        exit /b 1
    )
)

python -m venv "venv"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    popd >nul
    pause
    exit /b 1
)
echo       Done.
echo.

echo [2/3] Activating virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment activation script not found.
    popd >nul
    pause
    exit /b 1
)
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    popd >nul
    pause
    exit /b 1
)
echo       Done.
echo.

echo [3/3] Installing dependencies...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found.
    popd >nul
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r "requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    popd >nul
    pause
    exit /b 1
)
echo       Done.
echo.

echo [4/4] Ensuring model files are present...
if not exist "models" mkdir "models"

if not exist "models\hand_landmarker.task" (
    echo       Downloading MediaPipe hand model...
    python -c "import os,urllib.request; os.makedirs('models', exist_ok=True); urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task','models/hand_landmarker.task')"
    if errorlevel 1 (
        echo [ERROR] Failed to download hand_landmarker.task
        popd >nul
        pause
        exit /b 1
    )
) else (
    echo       hand_landmarker.task already exists.
)
echo       Done.
echo.

echo ============================================================
echo   SETUP COMPLETE!
echo.
echo   To run the application:
echo     run.bat
echo ============================================================
echo.

popd >nul
pause
exit /b 0
