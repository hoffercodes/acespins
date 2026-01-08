import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time

def perform_login(game_id="orion"):
    session = requests.Session()
    session.headers.update(config.HEADERS)
    
    print(f"--- STARTING LOGIN FOR {game_id} ---")

    MAX_RETRIES = 3
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt} of {MAX_RETRIES}...")

            # 1. Get Login Page
            # We add verify=False just in case the site has SSL issues
            resp = session.get(config.LOGIN_URL, timeout=15) # removed verify=False to keep it standard first
            
            # DEBUG: Print exactly what happened
            print(f"Page Status: {resp.status_code}") 
            
            if resp.status_code != 200:
                print(f"❌ Site rejected us. Code: {resp.status_code}")
                time.sleep(2)
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 2. Extract Hidden Fields
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})

            if not viewstate:
                # If we get 200 OK but no fields, maybe it's a "Cloudflare" or "Maintenance" page
                print(f"❌ Page loaded but form missing. Title: {soup.title.string if soup.title else 'No Title'}")
                time.sleep(1)
                continue

            # 3. Solve Captcha
            captcha_code = captcha_solver.get_captcha_code(session)
            print(f"--> Solved Captcha: {captcha_code}")

            if not captcha_code:
                print("❌ Captcha unreadable. Retrying...")
                time.sleep(1)
                continue

            # 4. Submit
            payload = {
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_gen['value'],
                '__EVENTVALIDATION': ev_validation['value'] if ev_validation else "",
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'btnLogin': 'Login',
                'txtYzm': captcha_code
            }
            
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=20)
            
            if "Module/AccountManager/AccountsList.aspx" in post_resp.text or post_resp.status_code == 302:
                 print("✅ LOGIN SUCCESS!")
                 return session 
            
            print("❌ Login Failed (Wrong Password/Captcha). Retrying...")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)
    
    print("❌ ALL RETRIES FAILED.")
    return None
