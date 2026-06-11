import os
import pandas as pd
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / 'data' / 'products.xlsx'
OUT_DIR = ROOT / 'packages_by_category'
README = ROOT / 'README_FOR_INTERN.md'
SETUP = ROOT / 'setup_and_run.bat'
RUNNER = ROOT / 'run_generator.bat'


def copy_repo_to(tmp_dir: Path):
    """Copy necessary project files into tmp_dir (excluding virtualenvs and caches)."""
    excludes = {'.venv', '.git', 'dist', 'build', '__pycache__', 'packages_by_category'}
    for item in ROOT.iterdir():
        if item.name in excludes:
            continue
        dest = tmp_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_excel(DATA_FILE)
    if 'Category' not in df.columns:
        print('ERROR: data/products.xlsx must contain a Category column')
        return

    grouped = df.groupby('Category')
    for category, group in grouped:
        safe_cat = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in category).strip()
        pkg_name = f"package_{safe_cat}.zip"
        pkg_path = OUT_DIR / pkg_name
        tmp_dir = OUT_DIR / f"tmp_full_{safe_cat}"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True)

        # Copy full project (necessary files) to tmp_dir
        copy_repo_to(tmp_dir)

        # Replace data/products.xlsx with filtered data for this category
        data_dir = tmp_dir / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        out_data = data_dir / 'products.xlsx'
        group.to_excel(out_data, index=False)

        # Ensure README and batch scripts are present
        shutil.copy(README, tmp_dir / README.name)
        shutil.copy(SETUP, tmp_dir / SETUP.name)
        shutil.copy(RUNNER, tmp_dir / RUNNER.name)

        # Remove large or irrelevant folders if present
        for to_remove in ['.venv', 'dist', 'build', '__pycache__']:
            p = tmp_dir / to_remove
            if p.exists():
                try:
                    if p.is_dir():
                        shutil.rmtree(p)
                    else:
                        p.unlink()
                except Exception:
                    pass

        # Create zip of the entire tmp_dir contents (preserve folder structure inside zip root)
        with zipfile.ZipFile(pkg_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(tmp_dir):
                for file in files:
                    absf = Path(root) / file
                    relf = absf.relative_to(tmp_dir)
                    zf.write(absf, arcname=str(relf))

        shutil.rmtree(tmp_dir)
        print(f"Created {pkg_path}")


if __name__ == '__main__':
    main()
