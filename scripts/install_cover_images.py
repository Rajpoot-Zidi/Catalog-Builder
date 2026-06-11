"""
Small helper to install cover images into images/branding/ with filenames used by the generator.

Usage:
  # Copy specific files
  python scripts/install_cover_images.py --logo path/to/logo.png --left path/to/left.jpg --right path/to/right.jpg

  # Or place your three files (any names) into images/to_import/ and run without args
  python scripts/install_cover_images.py

It copies files to:
  images/branding/logo.png
  images/branding/cover_left.jpg
  images/branding/cover_right.jpg

If a file exists it will be overwritten.
"""
import os
import shutil
import argparse

DEFAULT_SRC_DIR = os.path.join("images", "to_import")
DEST_DIR = os.path.join("images", "branding")

def ensure_dirs():
    os.makedirs(DEFAULT_SRC_DIR, exist_ok=True)
    os.makedirs(DEST_DIR, exist_ok=True)


def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
        print(f"Installed: {dest}")
    except Exception as e:
        print(f"Failed to copy {src} -> {dest}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Install cover images into images/branding/")
    parser.add_argument("--logo", help="Path to logo file (e.g. logo.png)")
    parser.add_argument("--left", help="Path to left cover image")
    parser.add_argument("--right", help="Path to right cover image")
    parser.add_argument("--src-dir", default=DEFAULT_SRC_DIR, help="Directory to search for images if not provided")
    args = parser.parse_args()

    ensure_dirs()

    logo_dest = os.path.join(DEST_DIR, "logo.png")
    left_dest = os.path.join(DEST_DIR, "cover_left.jpg")
    right_dest = os.path.join(DEST_DIR, "cover_right.jpg")

    # If explicit paths provided, use them
    if args.logo and args.left and args.right:
        copy_file(args.logo, logo_dest)
        copy_file(args.left, left_dest)
        copy_file(args.right, right_dest)
        return

    # Otherwise try to find files in src-dir
    files = [f for f in os.listdir(args.src_dir) if os.path.isfile(os.path.join(args.src_dir, f))]
    if not files:
        print(f"No files found in {args.src_dir}. Place your logo and two cover images there or pass explicit --logo/--left/--right paths.")
        return

    # Heuristics: prefer png for logo, jpg/jpeg for covers
    pngs = [f for f in files if f.lower().endswith('.png')]
    jpgs = [f for f in files if f.lower().endswith(('.jpg', '.jpeg'))]

    # Pick logo: prefer png, else any file
    if pngs:
        src_logo = os.path.join(args.src_dir, pngs[0])
    else:
        src_logo = os.path.join(args.src_dir, files[0])

    # Pick two cover images from jpgs (or remaining files)
    covers = []
    if len(jpgs) >= 2:
        covers = [os.path.join(args.src_dir, jpgs[0]), os.path.join(args.src_dir, jpgs[1])]
    else:
        # take first two non-logo files
        remaining = [f for f in files if os.path.join(args.src_dir, f) != src_logo]
        if len(remaining) >= 2:
            covers = [os.path.join(args.src_dir, remaining[0]), os.path.join(args.src_dir, remaining[1])]
        elif len(remaining) == 1:
            covers = [os.path.join(args.src_dir, remaining[0]), os.path.join(args.src_dir, remaining[0])]
        else:
            # fallback to using logo for covers if nothing else
            covers = [src_logo, src_logo]

    copy_file(src_logo, logo_dest)
    copy_file(covers[0], left_dest)
    copy_file(covers[1], right_dest)

if __name__ == '__main__':
    main()
