from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import io
import pytesseract

def get_captcha_code(session, custom_url=None, image_bytes=None):
    try:
        if image_bytes:
            img = Image.open(io.BytesIO(image_bytes))
        else:
            resp = session.get(custom_url, timeout=10, verify=False)
            img = Image.open(io.BytesIO(resp.content))

        # --- PRE-PROCESSING FOR 5-DIGIT ACCURACY ---
        img = img.convert("L")  # Grayscale
        
        # 1. Increase Contrast & Sharpness
        img = ImageEnhance.Contrast(img).enhance(2.5)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        
        # 2. Scale up (Tesseract handles larger images better)
        img = img.resize((img.width * 3, img.height * 3), Image.Resampling.LANCZOS)
        
        # 3. Threshold (Pure Black & White)
        # This kills the background noise
        img = img.point(lambda p: 0 if p < 140 else 255)

        # 4. Tesseract Configuration
        # --psm 7: Treat as a single line of text
        # whitelist: ONLY look for 0-123456789
        custom_config = r'--psm 7 -c tessedit_char_whitelist=0123456789'
        
        code = pytesseract.image_to_string(img, config=custom_config).strip()
        
        # Remove any non-digits that might have slipped through
        clean_code = "".join(filter(str.isdigit, code))
        
        print(f"Solver: Tesseract identified -> {clean_code}")
        return clean_code

    except Exception as e:
        print(f"Captcha Solver Error: {e}")
        return ""
