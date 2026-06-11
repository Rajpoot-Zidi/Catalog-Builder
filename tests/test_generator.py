import os
import shutil
import pytest
from scripts.config_loader import AppConfig
from scripts.data_parser import ProductModel
from scripts.pagination import PaginationEngine
from scripts.renderer import PDFRenderer
from jinja2 import Environment, FileSystemLoader

def test_full_pipeline(tmp_path):
    # 1. Setup mock configuration
    config = AppConfig()
    config.layout.renderer = "playwright" # We verify using playwright since it works out-of-the-box
    config.layout.show_toc = True
    config.layout.show_category_covers = True
    config.images.cache_dir = os.path.join(tmp_path, "cache")
    
    # 2. Setup mock product data
    products = [
        ProductModel(Category="Plates", SKU="PL-01", **{"Product Name": "Plates A", "Price": 10.99, "Image URL": "https://picsum.photos/id/10/200/200"}),
        ProductModel(Category="Plates", SKU="PL-02", **{"Product Name": "Plates B", "Price": 12.99, "Image URL": "https://picsum.photos/id/11/200/200"}),
        ProductModel(Category="Cutlery", SKU="CU-01", **{"Product Name": "Forks", "Price": 4.50, "Image URL": "https://picsum.photos/id/12/200/200"}),
    ]
    
    # 3. Pagination
    engine = PaginationEngine(config)
    pages, toc_entries = engine.paginate(products)
    
    # Total pages should cover (cover removed):
    # 1. TOC
    # 2. Cutlery Cover (Starts at 2)
    # 3. Cutlery Products (1 item)
    # 4. Plates Cover (Starts at 4)
    # 5. Plates Products (2 items)
    # Total: 5 pages
    assert len(pages) == 5
    assert pages[-1]["total_pages"] == 5
    assert toc_entries[0]["category"] == "Cutlery"
    assert toc_entries[0]["page_num"] == 2
    assert toc_entries[1]["category"] == "Plates"
    assert toc_entries[1]["page_num"] == 4
    
    # 4. Render HTML
    # Load templates from workspace directory
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("base.html")
    html_content = template.render(config=config, pages=pages, toc_entries=toc_entries)
    
    html_path = os.path.join(tmp_path, "catalog.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    assert os.path.exists(html_path)
    
    # Copy styles.css to temp path for HTML compilation
    shutil.copy("templates/styles.css", os.path.join(tmp_path, "styles.css"))
    
    # 5. Render PDF
    pdf_path = os.path.join(tmp_path, "catalog.pdf")
    renderer = PDFRenderer(config)
    
    success = renderer.render(html_path, pdf_path)
    assert success
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0
