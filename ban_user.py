# ban_user.py
import config

def execute(session, user):
    try:
        payload = {'nullityuserid': user['uid']}
        session.headers.update({'Referer': config.ACCOUNTS_LIST_URL, 'Origin': config.BASE_DOMAIN})
        
        resp = session.post(config.ACCOUNTS_LIST_URL, data=payload)
        
        if "session has expired" in resp.text: return {"status": "EXPIRED"}
        
        code = resp.text.split('|')[0]
        if code == "0": return {"status": "success", "state": "Active"}
        elif code == "1": return {"status": "success", "state": "Banned"}
        return {"status": "failed", "message": resp.text}

    except Exception as e:
        return {"status": "error", "message": str(e)}