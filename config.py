# config.py

# --- URLS ---
BASE_DOMAIN = "https://orionstars.vip:8781"
LOGIN_URL = f"{BASE_DOMAIN}/default.aspx"
CAPTCHA_URL = f"{BASE_DOMAIN}/Tools/VerifyImagePage.aspx" 
# FIX: The page we land on after a successful login
STORE_URL = f"{BASE_DOMAIN}/Store.aspx" 
ACCOUNTS_LIST_URL = f"{BASE_DOMAIN}/Module/AccountManager/AccountsList.aspx"
GRANT_URL = f"{BASE_DOMAIN}/Module/AccountManager/GrantTreasure.aspx"

# --- CREDENTIALS ---
USERNAME = "Antonyos666"
PASSWORD = "Hotspott123@@"

# --- HEADERS ---
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
