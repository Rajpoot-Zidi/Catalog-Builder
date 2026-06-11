import os
import shutil
import pytest
from PIL import Image
from scripts.image_manager import ImageManager

@pytest.fixture
def temp_cache_dir(tmp_path):
    cache_path = os.path.join(tmp_path, "cache")
    yield cache_path
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)

def test_placeholder_generation(temp_cache_dir):
    manager = ImageManager(cache_dir=temp_cache_dir)
    
    # 1. Default placeholder should be generated on init
    default_placeholder = os.path.join(temp_cache_dir, "placeholder.jpg")
    assert os.path.exists(default_placeholder)
    with Image.open(default_placeholder) as img:
        assert img.size == (400, 400)
        
    # 2. Custom SKU placeholder should be generated
    sku_placeholder = manager.get_placeholder_for_sku("SKU-999", "Super Catering Item")
    assert os.path.exists(sku_placeholder)
    assert f"placeholder_SKU-999.jpg" in sku_placeholder
    with Image.open(sku_placeholder) as img:
        assert img.size == (400, 400)

def test_image_process_missing_and_invalid(temp_cache_dir):
    manager = ImageManager(cache_dir=temp_cache_dir)
    
    # Missing local file reference -> should return SKU placeholder
    result = manager.process_image("images/missing_file_123.jpg", "SKU-MISSING", "Missing Item")
    assert os.path.exists(result)
    assert "placeholder_SKU-MISSING.jpg" in result

    # Invalid URL domain -> should return SKU placeholder
    result = manager.process_image("https://completely-fake-domain-12345.com/item.png", "SKU-FAKEURL", "Fake URL Item")
    assert os.path.exists(result)
    assert "placeholder_SKU-FAKEURL.jpg" in result
