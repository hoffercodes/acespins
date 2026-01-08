# login_manager.py
import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time

def perform_login(game_id="orion"):
    """
    Attempts to login in a loop until successful.
    Returns: requests.Session object once authenticated.
    """
    # 1. FIX: Create the session object explicitly here
    # (This prevents the 'str object has no attribute headers' crash)
    session = requests.Session()
    session.headers.update(config.HEADERS)
    
    print(f"Starting login for {game_id}...")

    # Start the Auto-Retry Loop
    while True:
        try:
            # A. Get Login Page
            resp = session.get(config.LOGIN_URL, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # B. Extract Hidden Form Fields
            viewstate_tag = soup.find("input", {"id": "__VIEWSTATE"})
            viewstate_gen_tag = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})
            ev_tag = soup.find("input", {"id": "__EVENTVALIDATION"})
            
            if not viewstate_tag: 
                time.sleep(1)
                continue

            # C. CALL THE CAPTCHA SOLVER
            # This uses the new captcha_solver.py you just uploaded
            captcha_code = captcha_solver.get_captcha_code(session)
            
            if not captcha_code:
                print("Captcha failed, retrying...")
                time.sleep(1)
                continue

            # D. Submit the Login Form
            payload = {
                '__VIEWSTATE': viewstate_tag['value'],
                '__VIEWSTATEGENERATOR': viewstate_gen_tag['value'],
                '__EVENTVALIDATION': ev_tag['value'] if ev_tag else "",
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'btnLogin': 'Login',
                'txtYzm': captcha_code # The solved code
            }
            
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=10)
            
            # E. Check if Login Worked
            if config.ACCOUNTS_LIST_URL in post_resp.url or \
               "Module/AccountManager/AccountsList.aspx" in post_resp.text or \
               post_resp.status_code == 302:
                 print("Login Successful!")
                 return session 
            
            # If we are here, login failed (probably wrong captcha)
            print("Login failed (Wrong Captcha?), retrying...")
            time.sleep(1)
            
        except Exception as e:
            print(f"Network Error: {e}")
            time.sleep(2)
            continue
