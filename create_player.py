# create_player.py
from bs4 import BeautifulSoup

def execute(session, url, username, password, nickname=None):
    try:
        resp = session.get(url)
        if "session has expired" in resp.text: return {"status": "EXPIRED"}
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        payload = {
            '__EVENTTARGET': 'ctl07', 
            '__EVENTARGUMENT': "",
            '__VIEWSTATE': soup.find("input", {"id": "__VIEWSTATE"})['value'],
            '__VIEWSTATEGENERATOR': soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value'],
            '__EVENTVALIDATION': soup.find("input", {"id": "__EVENTVALIDATION"})['value'],
            'txtAccount': username,
            'txtNickName': nickname if nickname else username,
            'txtLogonPass': password,
            'txtLogonPass2': password
        }

        post_resp = session.post(url, data=payload)
        
        if "session has expired" in post_resp.text: return {"status": "EXPIRED"}
        if "Added successfully" in post_resp.text: return {"status": "success", "message": "Created"}
        return {"status": "failed", "message": "Username likely exists"}

    except Exception as e:
        return {"status": "error", "message": str(e)}