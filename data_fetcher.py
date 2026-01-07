# data_fetcher.py
import re
from bs4 import BeautifulSoup
from datetime import datetime
import config
import login_manager

def extract_ids(tag):
    if not tag: return None, None
    text = tag.get('onclick', '') or tag.get('href', '')
    match = re.search(r"updateSelect\s*\(\s*['\"]([\d,]+)['\"]\s*\)", text)
    if match:
        parts = match.group(1).split(',')
        return parts[0].strip(), parts[1].strip()
    return None, None

def search_user(session, target_name):
    """
    Returns: {'username': '...', 'uid': '...', 'gid': '...', ...} OR None
    """
    params = {'timestamp': datetime.now().strftime("%-m/%-d/%Y %-I:%M:%S %p")}
    session.headers.update({'Referer': config.ACCOUNTS_LIST_URL, 'Origin': config.BASE_DOMAIN})

    try:
        get_resp = session.get(config.ACCOUNTS_LIST_URL, params=params)
        
        # Auto-Relogin check
        if "session has expired" in get_resp.text:
            login_manager.perform_login(session)
            get_resp = session.get(config.ACCOUNTS_LIST_URL, params=params)

        soup = BeautifulSoup(get_resp.text, 'html.parser')
        
        vs_tag = soup.find("input", {"id": "__VIEWSTATE"})
        if not vs_tag: return None

        payload = {
            '__EVENTTARGET': "ctl16",
            '__EVENTARGUMENT': "",
            '__VIEWSTATE': vs_tag['value'],
            '__VIEWSTATEGENERATOR': soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value'],
            '__EVENTVALIDATION': soup.find("input", {"id": "__EVENTVALIDATION"})['value'],
            'txtSearch': target_name, 
            'ShowHideAccount': "1"
        }
        
        resp = session.post(config.ACCOUNTS_LIST_URL, params=params, data=payload)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        rows = soup.find_all("tr")
        for row in rows:
            if target_name.lower() in row.text.lower():
                cols = row.find_all("td")
                if len(cols) >= 8:
                    btn = cols[0].find("a", onclick=lambda o: o and "updateSelect" in o)
                    uid, gid = extract_ids(btn)
                    return {
                        "username": cols[2].get_text(strip=True),
                        "id": cols[1].get_text(strip=True),
                        "credit": cols[3].get_text(strip=True),
                        "uid": uid,
                        "gid": gid
                    }
        return None
    except Exception:
        return None