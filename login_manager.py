# login_manager.py
import requests
from bs4 import BeautifulSoup
import config
import captcha_solver  
import time

def perform_login(session=None):
    """
    Attempts to login in a loop until successful.
    Returns: requests.Session object once authenticated.
    """
    if not session:
        session = requests.Session()
    
    session.headers.update(config.HEADERS)
    
    # Start the Auto-Retry Loop
    while True:
        try:
            # 1. Get Login Page for tokens
            resp = session.get(config.LOGIN_URL, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 2. Extract Tokens
            viewstate = soup.find("input", {"id": "__VIEWSTATE"})['value']
            viewstate_gen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value']
            ev_tag = soup.find("input", {"id": "__EVENTVALIDATION"})
            ev_val = ev_tag['value'] if ev_tag else ""
            
            # 3. Get Automatic Captcha Code
            captcha_code = captcha_solver.get_captcha_code(session)
            
            if not captcha_code:
                time.sleep(1) # Wait 1 sec before retrying if OCR failed
                continue

            # 4. Submit Credentials
            payload = {
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstate_gen,
                '__EVENTVALIDATION': ev_val,
                'txtCode': config.USERNAME,
                'txtPassword': config.PASSWORD,
                'btnLogin': 'Login',
                'txtYzm': captcha_code
            }
            
            post_resp = session.post(config.LOGIN_URL, data=payload, timeout=10)
            
            # 5. Check for Success
            success_indicators = [
                "Module/AccountManager/AccountsList.aspx",
                "Object moved"
            ]
            
            if any(ind in post_resp.text for ind in success_indicators) or post_resp.url == config.ACCOUNTS_LIST_URL:
                 return session # SUCCESS: Break loop and return session
            
            # If we reach here, login failed (wrong captcha or creds)
            time.sleep(1)
            
        except Exception:
            # If there's a network error, wait and try again
            time.sleep(2)
            continue