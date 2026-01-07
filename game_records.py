from bs4 import BeautifulSoup

def execute(session, url):
    try:
        resp = session.get(url)
        if "session has expired" in resp.text: 
            return {"status": "EXPIRED"}
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        game_history = []
        
        # Target the table rows for game data
        for row in soup.select('table.game-history tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:
                game_history.append({
                    "game_id": cols[0].text.strip(),
                    "type": cols[1].text.strip(),
                    "outcome": cols[2].text.strip().upper(), # WIN or LOSS
                    "profit": cols[3].text.strip()
                })
                
        return {"status": "success", "data": game_history}
    except Exception as e:
        return {"status": "error", "message": str(e)}