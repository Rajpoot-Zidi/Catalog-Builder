@echo off
REM build_exe.bat - Build a standalone Windows folder using PyInstaller and bundle Playwright browsers
REM Usage: Run this on a Windows build machine that has Python installed.

setlocal enabledelayedexpansion
set VENV=.build-venv
set DIST_DIR=dist
set APP_NAME=catalog_app

echo Creating build virtual environment in %VENV%...
if not exist %VENV% (
  python -m venv %VENV%
)

call %VENV%\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

echo Installing Playwright browsers (required for PDF rendering)...
python -m playwright install --with-deps

echo Running PyInstaller (one-folder build)...
pyinstaller --noconfirm --onedir ^
  --name %APP_NAME% ^
  --add-data "templates;templates" ^
  --add-data "config;config" ^
  --add-data "data;data" ^
  --add-data "images;images" ^
  --add-data "output;output" ^
  --add-data "README_FOR_INTERN.md;." ^
  --hidden-import=playwright._impl._driver ^
  main.py

if %ERRORLEVEL% neq 0 (
  echo PyInstaller failed. Exiting.
  exit /b %ERRORLEVEL%
)

REM Attempt to copy Playwright browser cache into the app folder so Playwright can run without internet
set PW_CACHE=%USERPROFILE%\.cache\ms-playwright
set APP_DIST=%DIST_DIR%\%APP_NAME%

if exist "%PW_CACHE%" (
  echo Copying Playwright browser artifacts from %PW_CACHE% to %APP_DIST%\ms-playwright ...
  xcopy "%PW_CACHE%" "%APP_DIST%\ms-playwright" /E /I /Y
) else (
  echo WARNING: Playwright browser cache not found at %PW_CACHE%.
  echo If you want a truly offline app, ensure you run `python -m playwright install` before building and re-run this script.
)

echo Build complete. Output folder: %APP_DIST%
endlocal
pause
