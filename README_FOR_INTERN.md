Quick start for non-technical users — Catalog Generator

This is a simple guide to run the Catalog Generator on Windows for users with little or no coding experience.

Two easy ways to share or run the catalog:

1) If you just need to view the catalog (EASIEST)
   - Open the provided PDF: open the file `output\catalog.pdf` in your web browser or Adobe Reader.
   - Or open the HTML version: open `output\catalog.html` in any browser.

2) If you need to re-generate the catalog from the data file (a bit more setup)
   - Requirements (one-time):
     - A Windows PC with internet access.
     - Python 3.10 or 3.11 installed from https://www.python.org/downloads/
       - During installation, check "Add Python to PATH".
   - Steps (automated):
     - Double-click `setup_and_run.bat` in the project root. This will:
       1. Create a virtual environment in `.venv`.
       2. Install Python packages listed in `requirements.txt`.
       3. Download Playwright browser binaries.
       4. Run the generator to produce `output\catalog.html` and `output\catalog.pdf`.
     - When finished, the script will attempt to open the generated PDF automatically.

Notes & Troubleshooting
- If the script fails at the "playwright install" step, you likely have a firewall or no internet. You can skip PDF rendering by opening `output\catalog.html` in the browser.
- If Python is not installed, the script will show an error. Install Python (see above) then re-run `setup_and_run.bat`.
- If the generator cannot find images, check `images/cache/` and `images/branding/` folders. Placing final images into `images/cache/` with the same filenames (as used in templates) will avoid downloads.

What you can change safely
- Edit `data/products.xlsx` to add or update products. Keep the column names: "Category", "SKU", "Product Name", "Price", "Image URL".
- You do not need to touch any Python files.

If you want me to prepare a fully standalone Windows executable (so the intern doesn't need Python), tell me and I will create a packaged build using PyInstaller and include Playwright browsers.

Contact the repo owner if you run into problems — include the error text you see so we can help.

Batch files for one-click usage
- `setup_and_run.bat` — creates a virtual environment, installs requirements and runs the generator. Double-click this once to prepare the machine and generate outputs.
- `run_generator.bat` — re-runs the generator using the prepared virtual environment (useful after edits or new data).

Double-click the `.bat` files in Windows Explorer. If you'd like macOS or Linux scripts instead, I can add those as well.
