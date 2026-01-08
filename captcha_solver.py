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
    try:
        custom_config = f'--psm {psm_mode} -c tessedit_char_whitelist=0123456789'
        text = pytesseract.image_to_string(img, config=custom_config)
        return text.strip().replace(" ", "").replace("\n", "")
    except Exception as e:
        return ""

# UPDATE: Added 'custom_url' parameter
def get_captcha_code(session, custom_url=None):
    """
    Downloads captcha from a specific URL if provided, otherwise uses config.
    """
    target_url = custom_url if custom_url else config.CAPTCHA_URL
    timestamp = str(int(time.time() * 1000))
    
    print(f"Downloading Captcha from: {target_url}")
    
    try:
        # 1. Download Image
        response = session.get(target_url, params={timestamp: ""}, timeout=10)
        if response.status_code != 200:
            print(f"❌ Captcha Download Failed: Status {response.status_code}")
            return ""
            
        original_img = Image.open(io.BytesIO(response.content))
        
        # --- ATTEMPT 1: Standard ---
        img1 = original_img.resize((original_img.width * 3, original_img.height * 3), Image.Resampling.LANCZOS)
        img1 = img1.convert("L")
        img1_thresh = img1.point(lambda p: 255 if p > 150 else 0)
        
        code = solve_with_tesseract(img1_thresh, 8)
        if len(code) == 5: return code

        # --- ATTEMPT 2: Inverted ---
        img2 = ImageOps.invert(img1)
        img2_thresh = img2.point(lambda p: 255 if p > 140 else 0)
        code = solve_with_tesseract(img2_thresh, 8)
        if len(code) == 5: return code

        # --- ATTEMPT 3: Denoised ---
        img3 = img1.filter(ImageFilter.MedianFilter(3))
        img3 = img3.point(lambda p: 255 if p > 160 else 0)
        code = solve_with_tesseract(img3, 7)
        if len(code) == 5: return code
        
        # --- ATTEMPT 4: Raw ---
        code = solve_with_tesseract(original_img, 8)
        if len(code) == 5: return code

    except Exception as e:
        print(f"Captcha Error: {e}")
        
    return "" 
