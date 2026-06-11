import os
import hashlib
import requests
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Dict, Any

class ImageManager:
    def __init__(self, cache_dir: str = "images/cache", max_width: int = 600, max_height: int = 600, quality: int = 85,
                 basic_auth: Optional[Tuple[str, str]] = None,
                 login_flow: Optional[Dict[str, Any]] = None):
        self.cache_dir = cache_dir
        self.max_width = max_width
        self.max_height = max_height
        self.quality = quality
        # Optional authentication support
        # basic_auth: (username, password) for HTTP Basic Auth
        # login_flow: dict with keys: login_url, payload (dict), optional headers
        self.basic_auth = basic_auth
        self.login_flow = login_flow
        # Use a session to support cookies and persistent auth
        self._session = requests.Session()

        # If a login flow is provided, attempt to login now (non-fatal)
        if self.login_flow and isinstance(self.login_flow, dict):
            try:
                login_url = self.login_flow.get("login_url")
                payload = self.login_flow.get("payload", {})
                headers = self.login_flow.get("headers", {"User-Agent": "Mozilla/5.0"})
                if login_url:
                    resp = self._session.post(login_url, data=payload, headers=headers, timeout=10)
                    if not resp.ok:
                        print(f"Warning: login flow failed (status {resp.status_code}) for {login_url}")
            except Exception as e:
                print(f"Warning: Exception during login flow: {e}")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Define paths
        self.placeholder_path = os.path.join(self.cache_dir, "placeholder.jpg")
        self._ensure_default_placeholder()

    def _ensure_default_placeholder(self):
        """Generates a default placeholder image if it doesn't exist."""
        if os.path.exists(self.placeholder_path):
            return

        # Create a light gray square image
        width, height = 400, 400
        img = Image.new("RGB", (width, height), color="#f1f5f9")
        draw = ImageDraw.Draw(img)

        # Draw a double border
        draw.rectangle([10, 10, width - 10, height - 10], outline="#cbd5e1", width=2)
        draw.rectangle([15, 15, width - 15, height - 15], outline="#e2e8f0", width=1)

        # Draw a simple geometric camera icon placeholder
        # Body
        draw.rectangle([150, 180, 250, 240], fill="#e2e8f0", outline="#94a3b8", width=2)
        # Lens
        draw.ellipse([175, 185, 225, 235], fill="#f1f5f9", outline="#94a3b8", width=2)
        # Flash
        draw.rectangle([230, 170, 242, 179], fill="#94a3b8")

        # Try to write text
        text = "IMAGE NOT AVAILABLE"
        try:
            # Try load default bitmap font
            draw.text((width // 2, 280), text, fill="#64748b", anchor="ms")
        except Exception:
            # Fallback text draw if anchor is not supported on older PIL versions
            draw.text((width // 2 - 80, 275), text, fill="#64748b")

        img.save(self.placeholder_path, "JPEG", quality=85)
        print("Generated default placeholder image.")

    def get_placeholder_for_sku(self, sku: str, product_name: str) -> str:
        """Generates a custom placeholder image specific to a product SKU to look more professional."""
        custom_placeholder = os.path.join(self.cache_dir, f"placeholder_{sku}.jpg")
        if os.path.exists(custom_placeholder):
            return custom_placeholder
            
        width, height = 400, 400
        img = Image.new("RGB", (width, height), color="#f8fafc")
        draw = ImageDraw.Draw(img)

        # Draw elegant borders
        draw.rectangle([10, 10, width - 10, height - 10], outline="#e2e8f0", width=2)
        
        # Text labels
        try:
            draw.text((width // 2, 120), "NO IMAGE", fill="#94a3b8", anchor="ms")
            draw.text((width // 2, 200), sku, fill="#475569", anchor="ms")
            # Truncate long names
            disp_name = product_name[:25] + "..." if len(product_name) > 25 else product_name
            draw.text((width // 2, 260), disp_name, fill="#64748b", anchor="ms")
        except Exception:
            # Simple fallback
            draw.text((width // 2 - 40, 115), "NO IMAGE", fill="#94a3b8")
            draw.text((width // 2 - 30, 195), sku, fill="#475569")
            draw.text((width // 2 - 60, 255), product_name[:18], fill="#64748b")

        img.save(custom_placeholder, "JPEG", quality=85)
        return custom_placeholder

    def _is_url(self, path: str) -> bool:
        """Checks if a string is a web URL."""
        parsed = urlparse(path)
        return bool(parsed.scheme and parsed.netloc)

    def _get_url_extension(self, url: str) -> str:
        """Guesses the image extension from a URL."""
        path = urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            return ext
        return ".jpg" # Default fallback extension

    def process_image(self, image_ref: str, sku: str, product_name: str) -> str:
        """
        Processes an image reference (URL or local path).
        Downloads if remote, validates, compresses/resizes, and caches it.
        Returns the path to the cached/processed image.
        If loading fails, returns the path to a custom SKU placeholder.
        """
        if not image_ref or str(image_ref).strip() == "":
            return self.get_placeholder_for_sku(sku, product_name)

        image_ref = str(image_ref).strip()

        # If user already placed a final image into the cache directory, prefer it and skip processing.
        # Check exact filename in cache first (images/cache/<image_ref>)
        cache_candidate = os.path.join(self.cache_dir, os.path.basename(image_ref))
        if os.path.exists(cache_candidate):
            return cache_candidate

        # Also support placing SKU-named files directly in cache with common extensions
        common_exts = [".jpg", ".jpeg", ".png", ".webp"]
        for ext in common_exts:
            sku_candidate = os.path.join(self.cache_dir, f"{sku}{ext}")
            if os.path.exists(sku_candidate):
                return sku_candidate
        
        # Generate target cached path
        # Hash the reference to prevent conflicts, keeping the original extension
        ref_hash = hashlib.md5(image_ref.encode('utf-8')).hexdigest()
        
        if self._is_url(image_ref):
            ext = self._get_url_extension(image_ref)
            temp_path = os.path.join(self.cache_dir, f"temp_{ref_hash}{ext}")
            cached_path = os.path.join(self.cache_dir, f"cached_{ref_hash}{ext}")
            
            if os.path.exists(cached_path):
                return cached_path
                
            # Download file (support basic auth or session login)
            try:
                # 10 second timeout
                headers = {"User-Agent": "Mozilla/5.0"}
                # If basic_auth provided, use it directly for this request
                if self.basic_auth:
                    response = requests.get(image_ref, timeout=10, headers=headers, auth=self.basic_auth)
                else:
                    # Use session (may have cookies from login_flow)
                    response = self._session.get(image_ref, timeout=10, headers=headers)

                if response.status_code == 200:
                    with open(temp_path, "wb") as f:
                        f.write(response.content)
                    source_path = temp_path
                else:
                    print(f"Warning: Failed to download {image_ref} (HTTP {response.status_code})")
                    return self.get_placeholder_for_sku(sku, product_name)
            except Exception as e:
                print(f"Warning: Exception downloading {image_ref}: {e}")
                return self.get_placeholder_for_sku(sku, product_name)
        else:
            # Local file reference
            source_path = image_ref
            ext = os.path.splitext(source_path)[1].lower()
            cached_path = os.path.join(self.cache_dir, f"cached_{ref_hash}{ext}")
            
            if os.path.exists(cached_path):
                return cached_path
                
            if not os.path.exists(source_path):
                # Try relative to catalog workspace or data directory
                possible_paths = [
                    os.path.join("data", source_path),
                    os.path.join("images", source_path),
                    os.path.abspath(source_path)
                ]
                found = False
                for p in possible_paths:
                    if os.path.exists(p):
                        source_path = p
                        found = True
                        break
                if not found:
                    print(f"Warning: Local image not found: {image_ref}")
                    return self.get_placeholder_for_sku(sku, product_name)

        # Compress and process the image (from source_path to cached_path)
        try:
            with Image.open(source_path) as img:
                # Convert palette/RGBA modes appropriately if converting to JPEG
                # For WebP and PNG, we can preserve transparency
                save_format = img.format
                
                # Check dimensions
                if img.width > self.max_width or img.height > self.max_height:
                    img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
                
                # Optimize save parameters
                if save_format == "JPEG" or cached_path.endswith((".jpg", ".jpeg")):
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(cached_path, "JPEG", quality=self.quality, optimize=True)
                elif save_format == "PNG" or cached_path.endswith(".png"):
                    img.save(cached_path, "PNG", optimize=True)
                else:
                    # Default save
                    img.save(cached_path)
            
            # Clean up temp files if created
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
                
            return cached_path
        except Exception as e:
            print(f"Warning: Failed to process image {source_path}: {e}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return self.get_placeholder_for_sku(sku, product_name)
