import os
import yaml
from pydantic import BaseModel, Field

class CatalogConfig(BaseModel):
    title: str = "Product Catalog"
    subtitle: str = ""
    tagline: str = ""
    year: int = 2026
    website: str = ""
    logo_path: str = ""
    hero_image_path: str = ""

class GridConfig(BaseModel):
    columns: int = 3
    rows: int = 4

    @property
    def capacity(self) -> int:
        return self.columns * self.rows

class LayoutConfig(BaseModel):
    page_size: str = "A4"
    orientation: str = "portrait"
    grid: GridConfig = Field(default_factory=GridConfig)
    renderer: str = "auto"
    show_toc: bool = True
    show_category_covers: bool = True
    # If true, products are grouped and paginated by category. If false, products are
    # paginated sequentially across the catalog regardless of category.
    group_by_category: bool = True


class ThemeConfig(BaseModel):
    primary_color: str = "#1e293b"
    accent_color: str = "#b45309"
    text_color: str = "#0f172a"
    bg_color: str = "#ffffff"
    card_bg_color: str = "#f8fafc"
    font_family: str = "'Outfit', 'Inter', sans-serif"

class ImageConfig(BaseModel):
    cache_dir: str = "images/cache"
    max_width: int = 600
    max_height: int = 600
    quality: int = 85

class AppConfig(BaseModel):
    catalog: CatalogConfig = Field(default_factory=CatalogConfig)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    images: ImageConfig = Field(default_factory=ImageConfig)

def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    """Loads configuration from a YAML file and validates it."""
    if not os.path.exists(config_path):
        return AppConfig()
    
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
            return AppConfig(**data)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}. Using defaults.")
            return AppConfig()
