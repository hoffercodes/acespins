import io
import time
import requests
import config
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import os

# Windows path (ignore for Linux/Render)
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def solve_with_tesseract(img, psm_mode=8):
    """
    Tries to read digits from an image using specific Tesseract settings.
    """
    try:
        # whitelist 0-9 tells Tesseract to ONLY look for numbers
        custom_config = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(img, config=custom_config)
        # Remove spaces and newlines
        return text.strip().replace(" ", "").replace("\n", "")
    except Exception as e:
        print(f"Tesseract Error: {e}")
        return ""

def get_captcha_code(session):
    """
    Tries multiple filters to crack the captcha.
    """
    timestamp = str(int(time.time() * 1000))
    print("Downloading Captcha Image...")
    
    try:
        # 1. Download Image
        response = session.get(config.CAPTCHA_URL, params={timestamp: ""}, timeout=10)
        if response.status_code != 200:
            print(f"Captcha Download Failed: Status {response.status_code}")
            return ""
            
        original_img = Image.open(io.BytesIO(response.content))
        print(f"Image Downloaded. Size: {original_img.size}")

        # --- ATTEMPT 1: Standard High Contrast ---
        # Resize 3x for clarity
        img1 = original_img.resize((original_img.width * 3, original_img.height * 3), Image.Resampling.LANCZOS)
        img1 = img1.convert("L") # Grayscale
        # Simple threshold
        img1_thresh = img1.point(lambda p: 255 if p > 150 else 0)
        
        code = solve_with_tesseract(img1_thresh, 8)
        print(f"Scan 1 (Standard): '{code}'")
        if len(code) == 5: return code

        # --- ATTEMPT 2: Inverted Colors (Black text on White) ---
        img2 = ImageOps.invert(img1)
        img2_thresh = img2.point(lambda p: 255 if p > 140 else 0)
        
        code = solve_with_tesseract(img2_thresh, 8)
        print(f"Scan 2 (Inverted): '{code}'")
        if len(code) == 5: return code

        # --- ATTEMPT 3: Heavy Denoising (Blur dots) ---
        img3 = img1.filter(ImageFilter.MedianFilter(3)) # Blur small dots
        img3 = img3.point(lambda p: 255 if p > 160 else 0) # High contrast
        
        code = solve_with_tesseract(img3, 7) # Try PSM 7 (Line mode)
        print(f"Scan 3 (Denoised): '{code}'")
        if len(code) == 5: return code
        
        # --- ATTEMPT 4: Raw Image (No Filters) ---
        # Sometimes fewer filters is better
        code = solve_with_tesseract(original_img, 8)
        print(f"Scan 4 (Raw): '{code}'")
        if len(code) == 5: return code

    except Exception as e:
        print(f"Captcha Critical Error: {e}")
        
    print("❌ All scans failed.")
    return "" 
