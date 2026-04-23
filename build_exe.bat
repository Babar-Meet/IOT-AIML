@echo off
setlocal EnableExtensions

pushd "%~dp0" >nul

title Build Standalone Executable
echo ============================================================
echo   BUILDING STANDALONE IOT-AIML APP
echo ============================================================
echo.

if not exist "main.py" (
    echo [ERROR] main.py not found. Please run from the project folder.
    popd >nul
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Compile from python environment directly or run poetry shell.
) else (
    echo [*] Activating virtual environment...
    call "venv\Scripts\activate.bat"
)


echo [*] Installing PyInstaller...
python -m pip install "pyinstaller>=6.0"

echo [*] Cleaning old build outputs...
if exist "build" rmdir /s /q "build"
if exist "dist\IOT-AIML" rmdir /s /q "dist\IOT-AIML"

echo [*] Building executable with PyInstaller...
echo     This may take a few minutes as it packages dependencies...

python -m PyInstaller --name "IOT-AIML" --onedir --add-data "config.json;." --add-data "models;models" --hidden-import "mediapipe" --collect-data "mediapipe" --collect-binaries "mediapipe" --noconfirm "main.py"

if errorlevel 1 (
    echo [ERROR] PyInstaller failed during compilation.
    popd >nul
    pause
    exit /b 1
)

:: Copy models and config into dist folder if needed (redundant if --add-data worked but explicitly ensures availability)
xcopy /y "config.json" "dist\IOT-AIML\" >nul
xcopy /e /i /y "models" "dist\IOT-AIML\models" >nul

if not exist "dist\IOT-AIML\IOT-AIML.exe" (
    echo [ERROR] Build finished but executable not found.
    popd >nul
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD COMPLETE!
echo   The executable is located at:
echo   dist\IOT-AIML\IOT-AIML.exe
echo.
echo   You can copy the entire "dist\IOT-AIML" folder
echo   and run the .exe anywhere on Windows.
echo ============================================================

popd >nul
pause
exit /b 0
