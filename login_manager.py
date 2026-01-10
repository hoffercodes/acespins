import requests
from bs4 import BeautifulSoup
import time
import urllib3
import base64
from urllib.parse import urljoin
import config
import captcha_solver  

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def perform_login(game_id="orion"):
    session = requests.Session()
    session.headers = config.HEADERS.copy()
    
    # Map game IDs to URLs
    url_map = {
        "orion": "https://orionstars.vip:8781/default.aspx"
    }
    target_url = url_map.get(game_id, config.LOGIN_URL)

    print(f"--- STARTING LOGIN FOR {game_id.upper()} ---")
    MAX_RETRIES = 5
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}...")
            resp = session.get(target_url, timeout=15, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # --- CAPTCHA DETECTION ---
            captcha_bytes = None
            custom_url = None
            base64_img = soup.find('img', src=lambda x: x and x.startswith('data:image'))
            
            if base64_img:
                captcha_bytes = base64.b64decode(base64_img['src'].split(',')[1])
            else:
                img_tag = soup.find('img', src=lambda x: x and ('VerifyImagePage' in x or 'Image.aspx' in x))
                if img_tag:
                    custom_url = urljoin(target_url, img_tag['src'])

            captcha_code = captcha_solver.get_captcha_code(session, custom_url=custom_url, image_bytes=captcha_bytes)
            
            if not captcha_code:
                time.sleep(1)
                continue

            # --- ASP.NET STATE DATA ---
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})['value']
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value']
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})
            ev_val = ev_validation['value'] if ev_validation else ""

            # --- PAYLOAD (Including the btnLogin fix) ---
            payload = {
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstate_gen,
                '__EVENTVALIDATION': ev_val,
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'txtYzm': captcha_code,
                'btnLogin': 'Login', # The button we found
                'btnLogin.x': '45',
                'btnLogin.y': '12'
            }
            
            post_resp = session.post(target_url, data=payload, timeout=20, verify=False)
            
            if "Store.aspx" in post_resp.url or "Store.aspx" in post_resp.text:
                 print("✅ LOGIN SUCCESS!")
                 return session 
            
            print("⚠️ Login failed (likely wrong captcha). Retrying...")
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)
    
    return None
