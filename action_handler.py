# action_handler.py
import requests
from bs4 import BeautifulSoup
import config
import login_manager

# Import Modules
import credit
import debit
import resetpass
import unbind
import ban_user
import create_player
import game_records
import transaction_records

# --- HELPER: Link Generator ---
def _get_link(session, user, code):
    session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
    data = {'tourl': code, 'getpassuid': user['uid'], 'getpassgid': user['gid']}
    try:
        resp = session.post(config.ACCOUNTS_LIST_URL, data=data)
        if "session has expired" in resp.text: return "EXPIRED"
        link = resp.text.split('|')[0]
        if len(link) > 5:
            return f"{config.BASE_DOMAIN}/{link}" if not link.startswith("http") else link
    except: pass
    return None

# --- GENERIC EXECUTOR (Handles Expiry & Retries) ---
def _execute_safe(session, user, action_func, *args):
    """
    Runs an action. If session is expired, re-logs in and retries once.
    """
    for _ in range(2):
        result = action_func(session, user, *args)
        if result and isinstance(result, dict) and result.get("status") == "EXPIRED":
            login_manager.perform_login(session)
            continue # Retry
        return result
    return {"status": "error", "message": "Session failed to recover."}

# --- PUBLIC API FUNCTIONS (Call these from your App) ---

def login():
    return login_manager.perform_login()

def recharge(session, user, amount):
    return _execute_safe(session, user, _handle_money, "0", amount)

def redeem(session, user, amount):
    return _execute_safe(session, user, _handle_money, "1", amount)

def reset_password(session, user, new_password):
    return _execute_safe(session, user, _handle_reset, new_password)

def ban_unban(session, user):
    return _execute_safe(session, user, ban_user.execute)

def unbind_device(session, user):
    return _execute_safe(session, user, unbind.execute)

def create_new_player(session, username, password, nickname=None):
    # Pass 'None' for user, as creation is global, but we need session
    # Code '6' is usually the standard link for creating players
    return _execute_safe(session, None, _handle_create, username, password, nickname)

def download_game_records(session, user):
    return _execute_safe(session, user, _handle_download, "4", game_records.execute)

def download_trans_records(session, user):
    return _execute_safe(session, user, _handle_download, "3", transaction_records.execute)

# --- INTERNAL HANDLERS ---

def _handle_money(session, user, code, amount):
    url = _get_link(session, user, code)
    if url == "EXPIRED": return {"status": "EXPIRED"}
    if not url: return {"status": "error", "message": "Link generation failed"}
    
    if 'X-Requested-With' in session.headers: del session.headers['X-Requested-With']
    session.headers.update({'Referer': config.ACCOUNTS_LIST_URL})
    
    resp = session.get(url)
    if "session has expired" in resp.text: return {"status": "EXPIRED"}
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    if code == "0": return credit.execute(session, url, soup, amount)
    else: return debit.execute(session, url, soup, amount)

def _handle_reset(session, user, new_password):
    url = _get_link(session, user, "2")
    if url == "EXPIRED": return {"status": "EXPIRED"}
    if not url: return {"status": "error", "message": "Link failed"}

    if 'X-Requested-With' in session.headers: del session.headers['X-Requested-With']
    resp = session.get(url)
    if "session has expired" in resp.text: return {"status": "EXPIRED"}
    
    return resetpass.execute(session, url, BeautifulSoup(resp.text, 'html.parser'), new_password)

def _handle_create(session, _, username, password, nickname):
    # Getting the generic Create Player URL (Code 6)
    # We create a dummy user object if needed by _get_link, or just assume global access.
    # Often '6' works with any valid user ID or even 0. 
    # Let's try requesting the link directly.
    session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
    # Use config USERNAME as dummy context if specific user not provided? 
    # For safety, we need a valid context. If your app flows from a Search, pass that user. 
    # If purely global, we might need to search 'Antonyos' (self) first.
    # Assuming the app has a valid 'user' context usually. 
    # If not, let's try direct URL construction if standard:
    # url = f"{config.BASE_DOMAIN}/Module/AccountManager/CreateAccount.aspx" 
    # But usually it needs a param. Let's assume we pass a user context in _execute_safe.
    # If passed None, we might fail getting a fresh link. 
    # FIX: Apps usually call Create Player FROM the main screen. 
    # We will assume a static URL or previously fetched valid link logic.
    # For now, let's use the static URL found in your HTML file:
    url = f"{config.BASE_DOMAIN}/Module/AccountManager/CreateAccount.aspx"
    return create_player.execute(session, url, username, password, nickname)

def _handle_download(session, user, code, logic_func):
    url = _get_link(session, user, code)
    if url == "EXPIRED": return {"status": "EXPIRED"}
    return logic_func(session, url)