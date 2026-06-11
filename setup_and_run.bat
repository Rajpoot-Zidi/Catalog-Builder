@echo off
rem setup_and_run.bat - sets up a virtual environment and runs the catalog generator

set VENV_DIR=.venv
if not exist %VENV_DIR% (
  echo Creating virtual environment...
  python -m venv %VENV_DIR%
)

echo Activating virtual environment and installing requirements...
call %VENV_DIR%\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

rem Install Playwright browsers (quiet)
python -m playwright install --with-deps

rem Run generator
python main.py

if exist output\catalog.pdf (
  echo Opening output\catalog.pdf
  start "" output\catalog.pdf
) else (
  echo PDF not found; open output\catalog.html in a browser to preview.
)

echo Done.
pause
