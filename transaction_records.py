from bs4 import BeautifulSoup

def execute(session, url):
    try:
        resp = session.get(url)
        if "session has expired" in resp.text: 
            return {"status": "EXPIRED"}
        
        # Parse the HTML to find transaction rows
        soup = BeautifulSoup(resp.text, 'html.parser')
        transactions = []
        
        # Adjust 'table' or 'tr' selectors based on the actual site structure
        for row in soup.find_all('tr')[1:]:  # Skipping header
            cols = row.find_all('td')
            if len(cols) >= 3:
                transactions.append({
                    "date": cols[0].text.strip(),
                    "description": cols[1].text.strip(),
                    "amount": cols[2].text.strip()
                })
                
        return {"status": "success", "data": transactions}
    except Exception as e:
        return {"status": "error", "message": str(e)}