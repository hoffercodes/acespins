# config.py

# --- URLS ---
BASE_DOMAIN = "https://orionstars.vip:8781"
LOGIN_URL = f"{BASE_DOMAIN}/default.aspx"
# FIX: This URL was missing, but captcha_solver.py needs it!
CAPTCHA_URL = f"{BASE_DOMAIN}/Image.aspx" 
ACCOUNTS_LIST_URL = f"{BASE_DOMAIN}/Module/AccountManager/AccountsList.aspx"
GRANT_URL = f"{BASE_DOMAIN}/Module/AccountManager/GrantTreasure.aspx"

# --- CREDENTIALS ---
USERNAME = "Antonyos666"
PASSWORD = "Hotspott123@@"

# --- HEADERS ---
HEADERS = {
    'Host': "orionstars.vip:8781",
    'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': LOGIN_URL  # Added for extra safety (helps avoid bans)
}
