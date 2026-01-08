import io
import time
import requests
import config
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import os

# Set Tesseract path only for Windows (Local Testing)
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def solve_image(img, psm_mode):
    """
    Helper function to run Tesseract with specific settings
    """
    try:
        # Only allow numbers (0-9) and treat as single word (psm 8)
        custom_config = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(img, config=custom_config)
        clean_code = text.replace(" ", "").strip()
        
        # Validation: Must be exactly 5 digits
        if len(clean_code) == 5 and clean_code.isdigit():
            return clean_code
    except:
        pass
    return None

def get_captcha_code(session):
    """
    Tries 3 different image filters to read the captcha.
    """
    for attempt in range(3): # Try downloading a new image 3 times
        timestamp = str(int(time.time() * 1000))
        try:
            # 1. Download Image
            response = session.get(config.CAPTCHA_URL, params={timestamp: ""}, timeout=5)
            if response.status_code != 200:
                continue
                
            original_img = Image.open(io.BytesIO(response.content))
            
            # --- STRATEGY 1: Standard High Contrast ---
            # Resize 3x for clarity
            img1 = original_img.resize((original_img.width * 3, original_img.height * 3), Image.Resampling.LANCZOS)
            img1 = img1.convert("L") # Grayscale
            img1 = img1.point(lambda p: 255 if p > 140 else 0) # Threshold
            
            code = solve_image(img1, 8)
            if code: return code # Success!

            # --- STRATEGY 2: Inverted Colors (Sometimes helps Tesseract) ---
            img2 = ImageOps.invert(img1)
            code = solve_image(img2, 8)
            if code: return code 

            # --- STRATEGY 3: Heavy Noise Removal (Removes dots) ---
            img3 = original_img.resize((original_img.width * 4, original_img.height * 4), Image.Resampling.LANCZOS)
            img3 = img3.convert("L")
            img3 = img3.filter(ImageFilter.MedianFilter(3)) # Blurs out small dots
            img3 = img3.point(lambda p: 255 if p > 150 else 0) # Sharp threshold
            
            code = solve_image(img3, 7) # Try PSM 7 (Line of text) instead of 8
            if code: return code

        except Exception as e:
            print(f"Captcha Error: {e}")
            continue
            
    return "" # Failed after 3 downloads (9 total scans)
