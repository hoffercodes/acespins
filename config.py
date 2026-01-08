# config.py

# --- URLS ---
BASE_DOMAIN = "https://orionstars.vip:8781"
LOGIN_URL = f"{BASE_DOMAIN}/default.aspx"
# FIX: The file you uploaded proves THIS is the real captcha location
CAPTCHA_URL = f"{BASE_DOMAIN}/VerifyImagePage.aspx" 
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
