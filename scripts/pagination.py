from typing import List, Dict, Any, Tuple
from math import ceil
from scripts.data_parser import ProductModel
from scripts.config_loader import AppConfig

class PaginationEngine:
    def __init__(self, config: AppConfig):
        self.config = config
        self.cols = config.layout.grid.columns
        self.rows = config.layout.grid.rows
        self.grid_capacity = config.layout.grid.capacity

    def paginate(self, products: List[ProductModel]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Organizes products into pages.
        Returns:
            pages: List of dictionaries representing pages.
            toc_entries: List of category and page associations.
        """
        # 1. Group products by category (unless config requests sequential pagination)
        grouped_products: Dict[str, List[ProductModel]] = {}
        if self.config.layout.group_by_category:
            for product in products:
                cat = product.category
                if cat not in grouped_products:
                    grouped_products[cat] = []
                grouped_products[cat].append(product)
        else:
            # Put all products under a single synthetic category to paginate sequentially
            grouped_products["__ALL__"] = list(products)

        # 2. Sort categories and products within categories
        sorted_categories = sorted(list(grouped_products.keys()))
        for cat in sorted_categories:
            # Sort products by Name first, then SKU
            grouped_products[cat].sort(key=lambda p: (p.product_name, p.sku))

        # 3. Plan page structure
        pages: List[Dict[str, Any]] = []
        toc_entries: List[Dict[str, Any]] = []
        
        current_page_num = 1

        # (Cover page removed — start pagination with TOC or product pages)

        # Page 2: Table of Contents (Conditional)
        toc_page_index = None
        if self.config.layout.show_toc:
            toc_page_index = len(pages)
            pages.append({
                "page_num": current_page_num,
                "type": "toc",
                "title": "Table of Contents",
                "entries": [] # will fill this once we have page numbers
            })
            current_page_num += 1

        # Page 3+: Category Covers and Product Grids
        for category in sorted_categories:
            cat_products = grouped_products[category]
            
            # Record category cover starting page number
            toc_entries.append({
                "category": category,
                "page_num": current_page_num
            })

            # Category Cover Page (Conditional)
            if self.config.layout.show_category_covers:
                pages.append({
                    "page_num": current_page_num,
                    "type": "category_cover",
                    "category": category,
                    "product_count": len(cat_products)
                })
                current_page_num += 1

            # Category Product Pages
            num_product_pages = ceil(len(cat_products) / self.grid_capacity)
            for page_idx in range(num_product_pages):
                start_idx = page_idx * self.grid_capacity
                end_idx = start_idx + self.grid_capacity
                page_products = cat_products[start_idx:end_idx]

                pages.append({
                    "page_num": current_page_num,
                    "type": "products",
                    "category": category,
                    "products": page_products,
                    "grid_cols": self.cols,
                    "grid_rows": self.rows,
                    "current_part": page_idx + 1,
                    "total_parts": num_product_pages
                })
                current_page_num += 1

        # Update TOC entries in the TOC page if it exists
        if toc_page_index is not None:
            pages[toc_page_index]["entries"] = toc_entries

        # Set total page counts for footers
        total_pages = current_page_num - 1
        for page in pages:
            page["total_pages"] = total_pages
            
        print(f"Paginated {len(products)} products across {len(sorted_categories)} categories into {total_pages} total pages.")
        return pages, toc_entries
