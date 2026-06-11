import os
import pandas as pd
import random

def generate_sample_data(output_path: str = "data/products.xlsx", num_products: int = 50):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    categories = ["Cutlery", "Plates", "Drinkware", "Eco Packaging", "Catering Trays"]
    brands = ["EcoChoice", "Chefs Table", "BioSafe", "Elite Gourmet", "HydroGlass"]
    unit_sizes = ["Pack of 50", "Box of 100", "Set of 6", "1000 Pcs", "Case of 24", None]
    
    # Base products to generate random variations
    product_base = {
        "Cutlery": [
            "Wooden Forks", "Wooden Spoons", "Wooden Knives", "Bamboo Chopsticks", 
            "Cornstarch Teaspoons", "Compostable Cutlery Set", "Heavy Duty Silver Forks"
        ],
        "Plates": [
            "Sugarcane Round Plates 9 Inch", "Sugarcane Oval Platters", "Palm Leaf Square Plates", 
            "Compostable Paper Plates", "Bamboo Serving Platters", "Clear Plastic Dinner Plates"
        ],
        "Drinkware": [
            "Paper Coffee Cups 12oz", "Double Wall Kraft Cups", "Clear PLA Cold Cups 16oz", 
            "Biodegradable Paper Straws", "Glass Coffee Mugs", "Insulated Water Bottles"
        ],
        "Eco Packaging": [
            "Kraft Clamshell Boxes", "Sugarcane Burger Boxes", "Salad Bowls with PLA Lids", 
            "Paper Shopping Bags Large", "Greaseproof Sandwich Wraps", "Noodle Boxes 16oz"
        ],
        "Catering Trays": [
            "Aluminum Foil Trays Large", "Foil Lids for Catering Trays", "Black Plastic Platters", 
            "Clear Dome Lids", "Cardboard Catering Boxes"
        ]
    }
    
    data = []
    
    for i in range(1, num_products + 1):
        cat = random.choice(categories)
        base_name = random.choice(product_base[cat])
        sku = f"{cat[:3].upper()}-{i:03d}"
        
        # Add random flavor
        name = f"{base_name} ({random.choice(['Premium', 'Classic', 'Value', 'Eco-friendly', 'Heavy Duty'])})"
        
        price = round(random.uniform(2.99, 149.99), 2)
        
        # Mix of valid images, local references, and broken URLs
        img_choice = random.random()
        if img_choice < 0.6:
            # Valid remote image (Picsum returns a random image)
            # Use specific seed to test caching (same URL should cache)
            seed_id = i % 10 # 10 unique images to test cache sharing and hit rate
            img_url = f"https://picsum.photos/id/{10 + seed_id}/400/400"
        elif img_choice < 0.8:
            # Local image reference (deliberately missing to trigger SKU placeholder generation)
            img_url = f"images/local_product_{sku}.jpg"
        else:
            # Broken remote URL to test download failure handling
            img_url = f"https://invalid-domain-testing-12345.com/sku-{sku}.png"
            
        brand = random.choice(brands)
        unit = random.choice(unit_sizes)
        prod_code = f"CODE-{random.randint(10000, 99999)}"
        desc = f"High-quality {name.lower()} suitable for commercial catering and events."
        
        data.append({
            "Category": cat,
            "SKU": sku,
            "Product Name": name,
            "Price": price,
            "Image URL": img_url,
            "Brand": brand,
            "Unit Size": unit,
            "Product Code": prod_code,
            "Barcode": f"5012345{random.randint(100000, 999999)}",
            "Description": desc
        })
        
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)
    print(f"Generated sample product catalog database at: {output_path}")

if __name__ == "__main__":
    generate_sample_data(num_products=50)
