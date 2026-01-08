import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time

def perform_login(game_id="orion"):
    session = requests.Session()
    session.headers.update(config.HEADERS)
    
    print(f"--- STARTING LOGIN FOR {game_id} ---")

    # CONFIG: How many times to try before giving up?
    # 3 attempts is safe for a 120s timeout limit.
    MAX_RETRIES = 3
    
    # 🔄 THE RETRY LOOP
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt} of {MAX_RETRIES}...")

            # 1. Get Login Page (with timeout)
            resp = session.get(config.LOGIN_URL, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 2. Extract Hidden Fields
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})

            if not viewstate:
                print("❌ Failed to load page. Retrying...")
                time.sleep(1)
                continue

            # 3. Solve Captcha (Using your fast solver)
            captcha_code = captcha_solver.get_captcha_code(session)
            
            if not captcha_code:
                print("❌ Captcha empty/unreadable. Retrying...")
                time.sleep(1)
                continue

            print(f"--> Submitting Code: {captcha_code}")

            # 4. Submit Credentials
            payload = {
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_gen['value'],
                '__EVENTVALIDATION': ev_validation['value'] if ev_validation else "",
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'btnLogin': 'Login',
                'txtYzm': captcha_code
            }
            
            # Post with a 15-second timeout
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=15)
            
            # 5. Check Success
            # If we see the "AccountsList" page, we are IN!
            if "Module/AccountManager/AccountsList.aspx" in post_resp.text or post_resp.status_code == 302:
                 print("✅ LOGIN SUCCESS!")
                 return session 
            
            print("❌ Login Failed (Wrong Password or Captcha). Retrying...")
            time.sleep(2) # Wait a bit before next attempt
            
        except Exception as e:
            print(f"❌ Network/Script Error: {e}")
            time.sleep(2)
    
    # If the loop finishes without returning, we failed.
    print("❌ ALL RETRIES FAILED.")
    return None
