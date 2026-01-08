import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time
import urllib3

# Disable "Insecure Request" warnings for cleaner logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def perform_login(game_id="orion"):
    session = requests.Session()
    
    # --- STEP 1: FORCE CLEAN HEADERS (Ignore config.py) ---
    # We set these manually to guarantee they are perfect for the GET request.
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

            # 2. Get Login Page (SSL Verify False prevents handshake errors)
            resp = session.get(config.LOGIN_URL, timeout=15, verify=False)
            
            print(f"Page Status: {resp.status_code}") 
            
            if resp.status_code != 200:
                print(f"❌ Server rejected us. Code: {resp.status_code}")
                # If 500 error persists, we print headers to debug
                if resp.status_code == 500:
                    print(f"DEBUG Headers Sent: {session.headers}")
                time.sleep(2)
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 3. Extract Hidden Fields
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})

            if not viewstate:
                print("❌ Page loaded but form missing.")
                time.sleep(1)
                continue

            # 4. Solve Captcha
            captcha_code = captcha_solver.get_captcha_code(session)
            print(f"--> Solved Captcha: {captcha_code}")

            if not captcha_code:
                print("❌ Captcha unreadable. Retrying...")
                time.sleep(1)
                continue

            # 5. Submit Login (Add Form Headers NOW, not before)
            payload = {
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_gen['value'],
                '__EVENTVALIDATION': ev_validation['value'] if ev_validation else "",
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'btnLogin': 'Login',
                'txtYzm': captcha_code
            }
            
            # We add 'Content-Type' ONLY for this POST request
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
            
            print("❌ Login Failed (Wrong Password/Captcha). Retrying...")
            
            # Reset headers for next attempt (Clear the POST headers)
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
