# credit.py
def execute(session, url, soup, amount):
    try:
        btn = soup.find("input", type="submit") or soup.find("input", {"id": "Button1"})
        if not btn: return {"status": "error", "message": "Button not found"}

        payload = {
            '__EVENTTARGET': btn.get('name', 'Button1'),
            '__EVENTARGUMENT': "",
            '__VIEWSTATE': soup.find("input", {"id": "__VIEWSTATE"})['value'],
            '__VIEWSTATEGENERATOR': soup.find("input", {"id": "__VIEWSTATEGENERATOR"})['value'],
            '__EVENTVALIDATION': soup.find("input", {"id": "__EVENTVALIDATION"})['value'],
            'txtAddGold': str(amount),
            'txtReason': "App Recharge",
            'txtLeScore': soup.find("input", {"id": "txtLeScore"}).get('value', '0'),
            'txtYourScore': soup.find("input", {"id": "txtYourScore"}).get('value', '0')
        }

        resp = session.post(url, data=payload)
        
        if "session has expired" in resp.text: return {"status": "EXPIRED"}
        if "Confirmed successful" in resp.text: return {"status": "success", "message": "Recharge Successful"}
        return {"status": "failed", "message": "Check balance"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}