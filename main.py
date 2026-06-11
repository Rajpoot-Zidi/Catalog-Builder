import os
import sys
import time
import shutil
import argparse
from jinja2 import Environment, FileSystemLoader

from scripts.config_loader import load_config
from scripts.data_parser import load_products_from_file
from scripts.image_manager import ImageManager
from scripts.pagination import PaginationEngine
from scripts.renderer import PDFRenderer

def parse_args():
    parser = argparse.ArgumentParser(description="Catalog Automation Engine CLI")
    parser.add_argument(
        "--data", 
        type=str, 
        default="data/products.xlsx", 
        help="Path to the Excel or CSV product data file"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/config.yaml", 
        help="Path to the configuration YAML file"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="output/catalog.pdf", 
        help="Path to save the generated PDF catalog"
    )
    parser.add_argument(
        "--no-compress", 
        action="store_true", 
        help="Disable automatic image compression and optimization"
    )
    parser.add_argument(
        "--show-toc",
        dest="show_toc",
        action="store_true",
        help="Force showing the table of contents (overrides config)"
    )
    parser.add_argument(
        "--no-show-toc",
        dest="show_toc",
        action="store_false",
        help="Force hiding the table of contents (overrides config)"
    )
    parser.set_defaults(show_toc=None)
    parser.add_argument(
        "--show-category-covers",
        dest="show_category_covers",
        action="store_true",
        help="Force showing category cover pages (overrides config)"
    )
    parser.add_argument(
        "--no-show-category-covers",
        dest="show_category_covers",
        action="store_false",
        help="Force hiding category cover pages (overrides config)"
    )
    parser.set_defaults(show_category_covers=None)
    parser.add_argument(
        "--group-by-category",
        dest="group_by_category",
        action="store_true",
        help="Force grouping products by category (overrides config)"
    )
    parser.add_argument(
        "--no-group-by-category",
        dest="group_by_category",
        action="store_false",
        help="Force paginating products sequentially (overrides config)"
    )
    parser.set_defaults(group_by_category=None)
    # (Cover flags removed — cover pages are no longer part of the catalog)
    return parser.parse_args()

def main():
    args = parse_args()
    start_time = time.time()

    print("=" * 60)
    print("        CATALOG AUTOMATION ENGINE - GENERATING CATALOG")
    print("=" * 60)

    # 1. Load configuration
    print(f"Loading configuration from: {args.config}")
    config = load_config(args.config)

    # Override image compression if flag is passed
    if args.no_compress:
        config.images.max_width = 9999
        config.images.max_height = 9999
        config.images.quality = 100

    # Apply CLI overrides for structure options if provided
    if args.show_toc is not None:
        config.layout.show_toc = args.show_toc
    if args.show_category_covers is not None:
        config.layout.show_category_covers = args.show_category_covers
    if args.group_by_category is not None:
        config.layout.group_by_category = args.group_by_category

    # 2. Parse data
    print(f"Reading product data from: {args.data}")
    try:
        products = load_products_from_file(args.data)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to load data file: {e}")
        sys.exit(1)

    if not products:
        print("CRITICAL ERROR: No products loaded. Exiting.")
        sys.exit(1)

    # Ensure output directories exist
    output_dir = os.path.dirname(args.output) or "output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_html_path = os.path.join(output_dir, "catalog.html")

    # 3. Process Images
    print("Processing catalog images (downloading, compressing, caching)...")
    image_mgr = ImageManager(
        cache_dir=config.images.cache_dir,
        max_width=config.images.max_width,
        max_height=config.images.max_height,
        quality=config.images.quality
    )

    # Process brand logo, hero image, and cover images if present
    logo_rel = None
    # Prefer configured path; if missing, fall back to common branding filenames
    logo_candidates = []
    if config.catalog.logo_path:
        logo_candidates.append(config.catalog.logo_path)
    # common branding names
    logo_candidates.extend([
        os.path.join("images", "branding", "1761650806_ws-main-logo.png"),
        os.path.join("images", "branding", "logo.png"),
    ])
    for cand in logo_candidates:
        if os.path.exists(cand):
            print(f"Processing logo: {cand}")
            logo_abs = image_mgr.process_image(cand, "logo", "Brand Logo")
            logo_rel = os.path.relpath(logo_abs, start=output_dir).replace(os.sep, '/')
            break

    hero_rel = None
    if config.catalog.hero_image_path and os.path.exists(config.catalog.hero_image_path):
        print(f"Processing hero image: {config.catalog.hero_image_path}")
        hero_abs = image_mgr.process_image(config.catalog.hero_image_path, "hero", "Catalog Hero")
        hero_rel = os.path.relpath(hero_abs, start=output_dir).replace(os.sep, '/')

    # (Cover images removed — cover pages are no longer used)

    # Process product images
    total_products = len(products)
    for i, product in enumerate(products, 1):
        if i % 100 == 0 or i == 1 or i == total_products:
            print(f"  [{i}/{total_products}] Processing image for SKU: {product.sku}")
        
        # Process and replace image path with cached file path relative to output directory
        cached_abs = image_mgr.process_image(product.image_url, product.sku, product.product_name)
        product.image_url = os.path.relpath(cached_abs, start=output_dir).replace(os.sep, '/')

    # 4. Paginate
    print("Calculating page layout pagination in Python...")
    pagination_engine = PaginationEngine(config)
    pages, toc_entries = pagination_engine.paginate(products)

    # Update logo values for Jinja rendering on pages (cover pages removed)
    for page in pages:
        if page.get("type") == "cover":
            # Keep logo/hero assignment for backward-compatibility in case templates reference them
            page["logo"] = logo_rel
            page["hero_image"] = hero_rel

    # 5. Render HTML
    print("Compiling Jinja2 templates...")
    templates_dir = "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    try:
        template = env.get_template("base.html")
        html_content = template.render(
            config=config,
            pages=pages,
            toc_entries=toc_entries
        )
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to render Jinja2 templates: {e}")
        sys.exit(1)

    print(f"Writing intermediate HTML to: {output_html_path}")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Copy stylesheet to output folder for relative link rendering
    try:
        shutil.copy(os.path.join(templates_dir, "styles.css"), os.path.join(output_dir, "styles.css"))
    except Exception as e:
        print(f"Warning: Failed to copy styles.css to output directory: {e}")

    # 6. Render PDF
    print(f"Generating PDF catalog: {args.output}")
    renderer = PDFRenderer(config)
    try:
        renderer.render(output_html_path, args.output)
    except Exception as e:
        print(f"CRITICAL ERROR: PDF compilation failed: {e}")
        sys.exit(1)

    duration = time.time() - start_time
    print("=" * 60)
    print("        CATALOG GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Products Processed: {total_products}")
    print(f"Pages Generated:    {pages[-1]['total_pages']}")
    print(f"Output PDF:         {os.path.abspath(args.output)}")
    print(f"Time Elapsed:       {duration:.2f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    main()
