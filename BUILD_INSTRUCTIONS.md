PyInstaller build instructions

1) Purpose

   This file documents how to build a standalone Windows app for the Catalog Generator so the intern does not need Python installed.

2) Requirements

   - A Windows build machine with Python 3.10/3.11 installed and on PATH.
   - Sufficient disk space (~1-2 GB) to install dependencies and Playwright browsers.
   - Internet access to download packages and Playwright browser artifacts (unless you copy them manually).

3) Steps (high-level)

   1. From the repo root, run `build_exe.bat` (double-click or run in a terminal). The script will:
      - Create a temporary virtual environment `.build-venv`.
      - Install requirements and PyInstaller.
      - Install Playwright browsers.
      - Run PyInstaller to make a one-folder build (directory `dist\catalog_app`).
      - Attempt to copy Playwright browser cache into `dist\catalog_app\ms-playwright` so the built app runs without re-downloading browsers.

   2. After the build completes, zip the `dist\catalog_app` folder and share the zip with the intern.

4) Notes & caveats

   - Playwright browser artifacts are large. To make the built app truly offline, run `python -m playwright install --with-deps` before building so the browser cache exists under `%USERPROFILE%\.cache\ms-playwright` and the build script can copy it.
   - The resulting folder will be large (hundreds of MBs to 1+ GB depending on browsers included).
   - If you prefer a single-file exe, PyInstaller supports `--onefile` but Playwright and large binary blobs make it tricky; one-folder is more reliable.

5) Testing the built app

   - After zipping and extracting on a target machine, double-click `catalog_app\main.exe` to run. The app will generate `output\catalog.pdf` inside the extracted folder.

If you want, I can run the build steps here in the workspace (I can attempt a PyInstaller build), but it may take time and increase workspace size. Tell me if you want me to proceed building an exe now.