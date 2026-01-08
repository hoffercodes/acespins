import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time
import urllib3

# Disable warnings for verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def perform_login(game_id="orion"):
    session = requests.Session()
    # 1. Start with CLEAN headers (No Content-Type)
    session.headers.update(config.HEADERS)
    
    print(f"--- STARTING LOGIN FOR {game_id} ---")

    MAX_RETRIES = 3
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt} of {MAX_RETRIES}...")

            # 2. Get Login Page (SSL Verify DISABLED)
            # We disable SSL verify because game servers often have weak certificates
            resp = session.get(config.LOGIN_URL, timeout=15, verify=False)
            
            print(f"Page Status: {resp.status_code}") 
            
            if resp.status_code != 200:
                print(f"❌ Server rejected us. Code: {resp.status_code}")
                time.sleep(2)
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})

            if not viewstate:
                print("❌ Page loaded but form missing.")
                time.sleep(1)
                continue

            # 3. Solve Captcha
            captcha_code = captcha_solver.get_captcha_code(session)
            print(f"--> Solved Captcha: {captcha_code}")

            if not captcha_code:
                print("❌ Captcha unreadable. Retrying...")
                time.sleep(1)
                continue

            # 4. Prepare Login (Add POST Headers Here)
            payload = {
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_gen['value'],
                '__EVENTVALIDATION': ev_validation['value'] if ev_validation else "",
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'btnLogin': 'Login',
                'txtYzm': captcha_code
            }
            
            # Add the specific headers needed for form submission
            post_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': config.LOGIN_URL,
                'Origin': config.BASE_DOMAIN
            }
            
            # Update session headers just for this POST
            session.headers.update(post_headers)
            
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=20, verify=False)
            
            if "Module/AccountManager/AccountsList.aspx" in post_resp.text or post_resp.status_code == 302:
                 print("✅ LOGIN SUCCESS!")
                 return session 
            
            print("❌ Login Failed (Wrong Password/Captcha). Retrying...")
            # Reset headers for next attempt (remove Content-Type)
            session.headers = config.HEADERS.copy() 
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)
    
    print("❌ ALL RETRIES FAILED.")
    return None
