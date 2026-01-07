# resetpass.py
def execute(session, url, soup, new_password):
    try:
        btn = soup.find("input", type="submit") or soup.find("input", {"id": "Button1"})
        pass_input = soup.find("input", type="password")
        if not pass_input: return {"status": "error", "message": "Password field missing"}

        payload = {
            '__EVENTTARGET': btn.get('name', 'Button1'),
            '__EVENTARGUMENT': "",
            '__VIEWSTATE': soup.find("input", {"id": "__VIEWSTATE"})['value'],
            '__VIEWSTATEGENERATOR': soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value'],
            '__EVENTVALIDATION': soup.find("input", {"id": "__EVENTVALIDATION"})['value'],
            pass_input.get('id'): new_password, 
            'txtReason': "App Reset"
        }

        resp = session.post(url, data=payload)
        
        if "session has expired" in resp.text: return {"status": "EXPIRED"}
        if "Confirmed successful" in resp.text: return {"status": "success", "message": "Password Changed"}
        return {"status": "failed", "message": "Unknown error"}

    except Exception as e:
        return {"status": "error", "message": str(e)}