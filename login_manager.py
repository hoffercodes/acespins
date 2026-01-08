import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time
import urllib3
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def perform_login(game_id="orion"):
    session = requests.Session()
    
    # 1. Force Clean Headers
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
            
            # 3. AUTO-DETECT CAPTCHA URL (Fixes 404 Error)
            # We look for an image that contains 'Image.aspx' OR 'yzm' OR 'Code' in the source
            img_tag = soup.find('img', src=lambda x: x and ('Image.aspx' in x or 'yzm' in x or 'ode' in x))
            
            target_captcha_url = config.CAPTCHA_URL # Default fallback
            
            if img_tag:
                # Combine base domain with the found relative path
                target_captcha_url = urljoin(config.LOGIN_URL, img_tag['src'])
                print(f"--> Auto-Detected Captcha URL: {target_captcha_url}")
            else:
                print("--> ⚠️ Could not auto-detect URL. Using Config default.")

            # 4. Solve Captcha (Using the detected URL)
            captcha_code = captcha_solver.get_captcha_code(session, target_captcha_url)
            print(f"--> Solved Captcha: {captcha_code}")

            if not captcha_code:
                print("❌ Captcha unreadable. Retrying...")
                time.sleep(1)
                continue

            # 5. Extract Hidden Fields & Submit
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
            
            # Add POST headers
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
            
            # Reset headers for next loop
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
