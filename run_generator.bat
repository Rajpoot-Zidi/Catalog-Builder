@echo off
rem run_generator.bat - activate the existing venv and run the generator
set VENV_DIR=.venv
if not exist %VENV_DIR% (
  echo Virtual environment not found. Run setup_and_run.bat first.
  pause
  exit /b 1
)

call %VENV_DIR%\Scripts\activate.bat
python main.py %*

if exist output\catalog.pdf (
  start "" output\catalog.pdf
) else (
  echo PDF not found; check output\catalog.html
)

pause
