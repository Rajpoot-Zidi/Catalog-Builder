import os
from scripts.config_loader import AppConfig

class PDFRenderer:
    def __init__(self, config: AppConfig):
        self.config = config
        self.renderer_choice = config.layout.renderer.lower()
        self.page_size = config.layout.page_size
        self.landscape = config.layout.orientation.lower() == "landscape"

    def render(self, html_path: str, pdf_path: str) -> bool:
        """
        Compiles the HTML file at html_path into a PDF at pdf_path.
        Automatically chooses or falls back between WeasyPrint and Playwright.
        """
        html_abs_path = os.path.abspath(html_path)
        pdf_abs_path = os.path.abspath(pdf_path)

        success = False
        
        # Determine order of renderers
        renderers_to_try = []
        if self.renderer_choice == "weasyprint":
            renderers_to_try = ["weasyprint"]
        elif self.renderer_choice == "playwright":
            renderers_to_try = ["playwright"]
        else:
            # "auto" or other fallback
            renderers_to_try = ["weasyprint", "playwright"]

        for renderer in renderers_to_try:
            if renderer == "weasyprint":
                success = self._render_with_weasyprint(html_abs_path, pdf_abs_path)
                if success:
                    break
            elif renderer == "playwright":
                success = self._render_with_playwright(html_abs_path, pdf_abs_path)
                if success:
                    break
                    
        if not success:
            raise RuntimeError("All PDF rendering engines failed. See error logs above.")
        return True

    def _render_with_weasyprint(self, html_path: str, pdf_path: str) -> bool:
        """Attempts to render using WeasyPrint."""
        print("Attempting to render PDF using WeasyPrint...")
        try:
            import weasyprint
            # Weasyprint compile
            weasyprint.HTML(filename=html_path).write_pdf(pdf_path)
            print("Successfully rendered PDF with WeasyPrint.")
            return True
        except ImportError:
            print("Warning: weasyprint library is not imported.")
            return False
        except OSError as e:
            print(f"Warning: WeasyPrint OSError (missing native Cairo libraries?): {e}")
            return False
        except Exception as e:
            print(f"Warning: WeasyPrint error: {e}")
            return False

    def _render_with_playwright(self, html_path: str, pdf_path: str) -> bool:
        """Attempts to render using Playwright browser automation."""
        print("Attempting to render PDF using Playwright (Chromium Headless)...")
        try:
            from playwright.sync_api import sync_playwright
            
            file_url = f"file:///{html_path.replace(os.sep, '/')}"
            
            with sync_playwright() as p:
                # Launch chromium in headless mode
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to the local file URL and wait for it to load
                page.goto(file_url, wait_until="networkidle")
                
                # Render to PDF
                page.pdf(
                    path=pdf_path,
                    format=self.page_size,
                    landscape=self.landscape,
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"}
                )
                
                browser.close()
                
            print("Successfully rendered PDF with Playwright.")
            return True
        except Exception as e:
            print(f"Error: Playwright PDF rendering failed: {e}")
            return False
