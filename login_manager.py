import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time

def perform_login(game_id="orion"):
    session = requests.Session()
    session.headers.update(config.HEADERS)
    
    print(f"--- STARTING LOGIN FOR {game_id} ---")

    # FIX: Only try 5 times. Do NOT loop forever.
    MAX_RETRIES = 5
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}/{MAX_RETRIES}...")

            # 1. Get Login Page
            resp = session.get(config.LOGIN_URL, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})

            if not viewstate:
                print("❌ Failed to load login page. Retrying...")
                time.sleep(1)
                continue

            # 2. Solve Captcha
            captcha_code = captcha_solver.get_captcha_code(session)
            print(f"--> Solved Captcha: {captcha_code}")
            
            if not captcha_code:
                print("❌ Captcha empty. Retrying...")
                time.sleep(1)
                continue

            # 3. Send Login Request
            payload = {
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_gen['value'],
                '__EVENTVALIDATION': ev_validation['value'] if ev_validation else "",
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'btnLogin': 'Login',
                'txtYzm': captcha_code
            }
            
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=15)
            
            # 4. Check Success
            if "Module/AccountManager/AccountsList.aspx" in post_resp.text or post_resp.status_code == 302:
                 print("✅ LOGIN SUCCESS!")
                 return session 
            
            print("❌ Login Failed (Wrong Password or Captcha). Retrying...")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)
    
    # If we run out of tries, return None instead of crashing
    print("❌ ALL ATTEMPTS FAILED. STOPPING.")
    return None
