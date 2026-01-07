# unbind.py
import config

def execute(session, user):
    try:
        payload = {'unbinduserid': user['uid']}
        session.headers.update({'Referer': config.ACCOUNTS_LIST_URL, 'Origin': config.BASE_DOMAIN})
        
        resp = session.post(config.ACCOUNTS_LIST_URL, data=payload)
        
        if "session has expired" in resp.text: return {"status": "EXPIRED"}
        if resp.status_code == 200: return {"status": "success", "message": "Unbind command sent"}
        return {"status": "failed", "code": resp.status_code}

    except Exception as e:
        return {"status": "error", "message": str(e)}