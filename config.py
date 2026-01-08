# config.py

# --- URLS ---
BASE_DOMAIN = "https://orionstars.vip:8781"
LOGIN_URL = f"{BASE_DOMAIN}/default.aspx"
CAPTCHA_URL = f"{BASE_DOMAIN}/Tools/VerifyImagePage.aspx" 
STORE_URL = f"{BASE_DOMAIN}/Store.aspx" 
ACCOUNTS_LIST_URL = f"{BASE_DOMAIN}/Module/AccountManager/AccountsList.aspx"
GRANT_URL = f"{BASE_DOMAIN}/Module/AccountManager/GrantTreasure.aspx"

# --- CREDENTIALS ---
USERNAME = "Antonyos666"
PASSWORD = "Hotspott123@@"

# --- HEADERS (DESKTOP MODE) ---
# We switched to Windows 10 Chrome. This prevents mobile-specific errors.
HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
