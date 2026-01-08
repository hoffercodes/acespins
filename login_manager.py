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
            print(f"Page Status: {resp.status_code}") 
            
            if resp.status_code != 200:
                print(f"❌ Server rejected us. Code: {resp.status_code}")
                time.sleep(2)
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # --- NEW CAPTCHA FINDER LOGIC ---
            captcha_bytes = None
            custom_url = None
            
            # A. Check for Base64 Image (The most likely one!)
            base64_img = soup.find('img', src=lambda x: x and x.startswith('data:image'))
            
            if base64_img:
                print("--> Found Base64 Captcha Image!")
                try:
                    # Extract the part after the comma
                    img_data_str = base64_img['src'].split(',')[1]
                    captcha_bytes = base64.b64decode(img_data_str)
                    print("--> Successfully decoded Base64 image.")
                except Exception as e:
                    print(f"--> Failed to decode Base64: {e}")

            # B. If no Base64, look for a standard URL (Fallback)
            if not captcha_bytes:
                img_tag = soup.find('img', src=lambda x: x and ('Image.aspx' in x or 'yzm' in x or 'ode' in x))
                if img_tag:
                    custom_url = urljoin(config.LOGIN_URL, img_tag['src'])
                    print(f"--> Found Captcha URL: {custom_url}")
                else:
                    # C. Last Resort: Try to find ANY image in the main content area
                    # Sometimes they hide it in a div called 'validate' or 'captcha'
                    container = soup.find('div', {'id': lambda x: x and ('code' in x.lower() or 'yzm' in x.lower())})
                    if container:
                        fallback_img = container.find('img')
                        if fallback_img:
                             custom_url = urljoin(config.LOGIN_URL, fallback_img['src'])
                             print(f"--> Found Captcha in container: {custom_url}")

            # 3. Call Solver (Pass Bytes if we have them, URL if we don't)
            captcha_code = captcha_solver.get_captcha_code(session, custom_url=custom_url, image_bytes=captcha_bytes)
            print(f"--> Solved Captcha: {captcha_code}")

            if not captcha_code:
                print("❌ Captcha unreadable. Retrying...")
                time.sleep(1)
                continue

            # 4. Extract & Submit
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
                'btnLogin': 'Login',
                'txtYzm': captcha_code
            }
            
            post_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': config.LOGIN_URL,
                'Origin': config.BASE_DOMAIN
            }
            session.headers.update(post_headers)
            
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=20, verify=False)
            
            if "Module/AccountManager/AccountsList.aspx" in post_resp.text or post_resp.status_code == 302:
                 print("✅ LOGIN SUCCESS!")
                 return session 
            
            print("❌ Login Failed. Retrying...")
            
            # Reset headers
            session.headers = {
                'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive'
            }
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)
    
    print("❌ ALL RETRIES FAILED.")
    return None
