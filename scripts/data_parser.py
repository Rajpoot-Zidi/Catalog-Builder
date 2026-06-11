import os
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo

class ProductModel(BaseModel):
    category: str = Field(..., alias="Category")
    sku: str = Field(..., alias="SKU")
    product_name: str = Field(..., alias="Product Name")
    # Make price optional so catalogs without prices can be generated
    price: Optional[float] = Field(None, alias="Price")
    image_url: str = Field(..., alias="Image URL")
    
    # Optional fields
    description: Optional[str] = Field(None, alias="Description")
    barcode: Optional[str] = Field(None, alias="Barcode")
    product_code: Optional[str] = Field(None, alias="Product Code")
    unit_size: Optional[str] = Field(None, alias="Unit Size")
    brand: Optional[str] = Field(None, alias="Brand")

    # Custom validator to coerce price to float
    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v):
        # Allow missing/empty price (None or empty string) and keep it as None
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            if s == "" or s.lower() == "nan":
                return None
            # Strip currency signs if any
            s = s.replace("$", "").replace("€", "").replace("£", "").strip()
            # Handle commas as thousands or decimal separators depending on formatting
            if "," in s and "." in s:
                s = s.replace(",", "")
            elif "," in s and len(s.split(",")[-1]) == 2:
                # e.g. "12,99"
                s = s.replace(",", ".")
            v = s
        try:
            return None if v is None else float(v)
        except (ValueError, TypeError):
            raise ValueError(f"Price must be a valid number or empty, got: {v}")

    @field_validator("sku", "category", "product_name", "image_url", mode="before")
    @classmethod
    def stringify_and_strip(cls, v, info: ValidationInfo):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be null")
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        s = str(v).strip()
        if not s:
            raise ValueError(f"{info.field_name} cannot be empty")
        return s

    @field_validator("description", "barcode", "product_code", "unit_size", "brand", mode="before")
    @classmethod
    def coerce_optional_string(cls, v):
        if v is None:
            return None
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        s = str(v).strip()
        if not s or s.lower() == "nan":
            return None
        return s


def load_products_from_file(file_path: str) -> List[ProductModel]:
    """
    Loads products from an Excel (.xlsx) or CSV (.csv) file.
    Validates each record using Pydantic.
    Logs and skips invalid records.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Product file not found: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    try:
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Must be Excel or CSV.")
    except Exception as e:
        raise ValueError(f"Failed to read product file: {e}")

    # Standardize column headers by stripping whitespace
    df.columns = [str(c).strip() for c in df.columns]

    # Required column validation (price is optional now)
    required_cols = ["Category", "SKU", "Product Name", "Image URL"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        # Try case-insensitive matching if direct match failed
        col_mapping = {}
        for r_col in required_cols:
            for d_col in df.columns:
                if r_col.lower() == d_col.lower():
                    col_mapping[d_col] = r_col
        if len(col_mapping) == len(required_cols):
            df = df.rename(columns=col_mapping)
        else:
            raise ValueError(f"Missing required columns in data file: {missing_cols}. Existing columns: {list(df.columns)}")

    products: List[ProductModel] = []
    
    # Fill NaN values with None for proper pydantic parsing
    df_dict = df.to_dict(orient="records")
    
    for idx, row in enumerate(df_dict, start=2): # 1-indexed header, start row = 2
        # Clean nan values
        cleaned_row = {}
        for k, v in row.items():
            if pd.isna(v):
                cleaned_row[k] = None
            else:
                cleaned_row[k] = v

        try:
            product = ProductModel(**cleaned_row)
            products.append(product)
        except Exception as e:
            print(f"Warning: Row {idx} failed validation and was skipped: {e}")

    print(f"Successfully loaded {len(products)} of {len(df_dict)} rows from {file_path}.")
    return products
