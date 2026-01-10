import io
import pytesseract
from PIL import Image, ImageEnhance, ImageOps

def get_captcha_code(session, custom_url=None, image_bytes=None):
    """
    Downloads and cleans the image for Tesseract digit recognition.
    """
    try:
        # 1. Load Image
        if image_bytes:
            img = Image.open(io.BytesIO(image_bytes))
        else:
            # Must use the same session to get the correct captcha image
            resp = session.get(custom_url, verify=False, timeout=10)
            img = Image.open(io.BytesIO(resp.content))

        # 2. Advanced Pre-Processing for Orion Stars
        img = img.convert("L")  # Convert to Grayscale
        
        # Boost Contrast (Makes noise fade and digits dark)
        img = ImageEnhance.Contrast(img).enhance(2.5)
        
        # Scale up (Tesseract is much more accurate with larger text)
        img = img.resize((img.width * 3, img.height * 3), Image.Resampling.LANCZOS)
        
        # Thresholding: Turn the image into pure Black and White
        # Removes the "gray fuzz" background
        img = img.point(lambda p: 0 if p < 130 else 255)

        # 3. Tesseract Config
        # psm 7: Treats image as a single line of text
        # whitelist: Forces Tesseract to ONLY see digits 0-9
        custom_config = r'--psm 7 -c tessedit_char_whitelist=0123456789'
        
        raw_text = pytesseract.image_to_string(img, config=custom_config)
        
        # Clean up any whitespace or newlines
        clean_code = "".join(filter(str.isdigit, raw_text))
        
        print(f"   [Solver] Result: {clean_code}")
        return clean_code

    except Exception as e:
        print(f"   [Solver Error]: {e}")
        return ""
