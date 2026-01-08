import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time
import urllib3
import base64
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def perform_login(game_id="orion"):
    session = requests.Session()
    
    # 1. Clean Headers
    session.headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print(f"--- STARTING LOGIN FOR {game_id} ---")
    MAX_RETRIES = 3
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt} of {MAX_RETRIES}...")

            # 2. Load Page
            resp = session.get(config.LOGIN_URL, timeout=15, verify=False)
            if resp.status_code != 200:
                print(f"❌ Server rejected us. Code: {resp.status_code}")
                time.sleep(2)
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # --- CAPTCHA LOGIC ---
            captcha_bytes = None
            custom_url = None
            
            # Look for Base64 or URL
            base64_img = soup.find('img', src=lambda x: x and x.startswith('data:image'))
            if base64_img:
                try:
                    captcha_bytes = base64.b64decode(base64_img['src'].split(',')[1])
                except: pass
            
            if not captcha_bytes:
                img_tag = soup.find('img', src=lambda x: x and ('VerifyImagePage' in x or 'Image.aspx' in x or 'yzm' in x))
                if img_tag:
                    custom_url = urljoin(config.LOGIN_URL, img_tag['src'])
                    print(f"--> Found Captcha URL: {custom_url}")
                else:
                    custom_url = config.CAPTCHA_URL

            # 3. Solve Captcha
            captcha_code = captcha_solver.get_captcha_code(session, custom_url=custom_url, image_bytes=captcha_bytes)
            print(f"--> Solved Captcha: {captcha_code}")

            if not captcha_code:
                print("❌ Captcha unreadable. Retrying...")
                time.sleep(1)
                continue

            # 4. Submit (With "Button Click" Coordinates)
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})
            
            if not viewstate:
                print("❌ Form fields missing.")
                continue

            payload = {
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_gen['value'],
                '__EVENTVALIDATION': ev_validation['value'] if ev_validation else "",
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'txtYzm': captcha_code,
                # FIX: Add coordinates to simulate a real click on the image button
                'btnLogin.x': '45', 
                'btnLogin.y': '12'
            }
            
            post_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': config.LOGIN_URL,
                'Origin': config.BASE_DOMAIN
            }
            session.headers.update(post_headers)
            
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=20, verify=False)
            
            # 5. CHECK FOR SUCCESS OR SPECIFIC ERROR
            if "Module/AccountManager/AccountsList.aspx" in post_resp.text or post_resp.status_code == 302:
                 print("✅ LOGIN SUCCESS!")
                 return session 
            
            # DEBUG: Find the error message on the page!
            error_soup = BeautifulSoup(post_resp.text, 'html.parser')
            # Look for common error script alerts or spans
            alert_msg = error_soup.find("script", string=lambda x: x and "alert" in x)
            error_span = error_soup.find("span", {"style": lambda x: x and "red" in x})
            
            if alert_msg:
                print(f"⚠️ Website Alert: {alert_msg.string}")
            elif error_span:
                print(f"⚠️ Website Error: {error_span.get_text().strip()}")
            else:
                print(f"❌ Login Failed. Page Title: {error_soup.title.string if error_soup.title else 'Unknown'}")
            
            # Reset headers
            session.headers = config.HEADERS.copy()
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)
    
    print("❌ ALL RETRIES FAILED.")
    return None
