import requests
from bs4 import BeautifulSoup
import time
import urllib3
import login_manager
import captcha_solver
import config
from urllib.parse import urljoin

# Disable warnings for local/internal port 8781
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def perform_login(game_id="orion"):
    """
    Main login engine for Orion Stars (ASP.NET).
    """
    session = requests.Session()
    session.headers = config.HEADERS.copy()
    
    print(f"--- 🔔 STARTING LOGIN FOR: {game_id.upper()} ---")
    
    MAX_RETRIES = 5
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt} of {MAX_RETRIES}...")
            
            # 1. Get the Login Page
            response = session.get(config.LOGIN_URL, verify=False, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 2. ASP.NET State Extraction
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})['value']
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value']
            ev_validation = soup.find("input", {"id": "__EVENTVALIDATION"})
            ev_val = ev_validation['value'] if ev_validation else ""

            # 3. Solve the 5-Digit Captcha
            # Note: We pass the session so cookies stay synchronized
            captcha_code = captcha_solver.get_captcha_code(session, custom_url=config.CAPTCHA_URL)

            # Safety: Only proceed if the solver actually found 5 digits
            if not captcha_code or len(captcha_code) != 5:
                print(f"   [!] Solver returned '{captcha_code}'. Not 5 digits. Retrying...")
                time.sleep(1)
                continue

            # 4. Construct Payload (Matches your HTML inspection)
            # value="Login in", id="btnLogin"
            payload = {
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstate_gen,
                '__EVENTVALIDATION': ev_val,
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'txtYzm': captcha_code,
                'btnLogin': 'Login in',  # Match the 'value' attribute
                'btnLogin.x': '45',       # Simulated mouse click X
                'btnLogin.y': '12'        # Simulated mouse click Y
            }

            # 5. Submit the Form
            post_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': config.LOGIN_URL,
                'Origin': config.BASE_DOMAIN
            }
            
            login_resp = session.post(
                config.LOGIN_URL, 
                data=payload, 
                headers=post_headers, 
                verify=False, 
                timeout=20
            )

            # 6. Verify Success via URL Redirect or Page Content
            if "Store.aspx" in login_resp.url or "Store.aspx" in login_resp.text:
                print(f"✅ LOGIN SUCCESSFUL: Logged into {game_id}")
                return session
            
            print("   [!] Login failed (Check credentials or captcha accuracy).")
            time.sleep(1.5)

        except Exception as e:
            print(f"   [❌] Error during attempt {attempt}: {e}")
            time.sleep(2)

    print("❌ ALL LOGIN ATTEMPTS EXHAUSTED.")
    return None
