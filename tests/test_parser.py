import os
import pytest
import pandas as pd
from scripts.data_parser import load_products_from_file, ProductModel

def test_pydantic_product_coercion():
    # Test valid coercion of numbers and price formats
    raw_data = {
        "Category": "Test Cat",
        "SKU": 12345, # Numeric SKU to be coerced to string
        "Product Name": "Test Product",
        "Price": "$12.99", # Price with symbol to be coerced to float
        "Image URL": "http://example.com/test.jpg",
        "Barcode": 5012345678901, # Numeric Barcode to be coerced to string
        "Product Code": "PC-99"
    }
    
    product = ProductModel(**raw_data)
    assert product.sku == "12345"
    assert product.price == 12.99
    assert product.barcode == "5012345678901"
    assert product.product_code == "PC-99"

def test_load_products_from_file(tmp_path):
    # Create a temporary Excel file
    temp_excel = os.path.join(tmp_path, "test_products.xlsx")
    
    test_rows = [
        # Valid Row
        {
            "Category": "Cutlery",
            "SKU": "SKU-01",
            "Product Name": "Forks",
            "Price": 9.99,
            "Image URL": "images/forks.jpg",
            "Brand": "Eco",
            "Barcode": "1234"
        },
        # Row with missing SKU (should be skipped)
        {
            "Category": "Plates",
            "SKU": None,
            "Product Name": "Plates",
            "Price": 14.99,
            "Image URL": "images/plates.jpg",
            "Brand": "Eco",
            "Barcode": "5678"
        },
        # Row with invalid price format (should be skipped)
        {
            "Category": "Drinkware",
            "SKU": "SKU-02",
            "Product Name": "Cups",
            "Price": "InvalidPriceValue",
            "Image URL": "images/cups.jpg",
            "Brand": "Eco",
            "Barcode": "9012"
        }
    ]
    
    df = pd.DataFrame(test_rows)
    df.to_excel(temp_excel, index=False)
    
    products = load_products_from_file(temp_excel)
    
    # Assert that only the valid row is loaded
    assert len(products) == 1
    assert products[0].sku == "SKU-01"
    assert products[0].price == 9.99
    assert products[0].product_name == "Forks"
