# captcha_solver.py
import io
import time
import requests
import config
from PIL import Image, ImageOps, ImageFilter
import pytesseract

# Set Tesseract path for Windows (Adjust if your path is different)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_captcha_code(session):
    """
    Silent version: No printing, returns 5-digit code or empty string.
    """
    for _ in range(3): # Try up to 3 times per login attempt
        timestamp = str(int(time.time() * 1000))
        try:
            # 1. Fetch Captcha
            response = session.get(config.CAPTCHA_URL, params={timestamp: ""}, timeout=5)
            if response.status_code != 200:
                continue
                
            img = Image.open(io.BytesIO(response.content))
            
            # 2. Image Processing (High Res + Sharp)
            width, height = img.size
            img = img.resize((width * 4, height * 4), Image.Resampling.LANCZOS)
            img = img.filter(ImageFilter.MinFilter(1))
            img = img.filter(ImageFilter.SHARPEN)
            
            # 3. Binary Contrast
            img = img.convert("L")
            img = ImageOps.invert(img)
            img = img.point(lambda p: 255 if p > 130 else 0)

            # 4. OCR Processing
            custom_config = r'--psm 7 -c tessedit_char_whitelist=0123456789'
            text = pytesseract.image_to_string(img, config=custom_config)
            clean_code = text.replace(" ", "").strip()
            
            # Only return if it's the correct 5-digit format
            if len(clean_code) == 5 and clean_code.isdigit():
                return clean_code 
                
        except Exception:
            # Silently fail and try the next attempt
            continue
            
    return "" # Return empty if all 3 attempts fail