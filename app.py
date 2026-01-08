from flask import Flask, jsonify, request, make_response
from flask_cors import CORS 
import login_manager
import os

app = Flask(__name__)

# Nuclear CORS: Allows your Netlify site to communicate with Render
CORS(app)

@app.route('/', methods=['GET'])
def home():
    # This fixes the "Not Found" error you saw in the browser
    return "AceSpins Multi-Backend Engine: Active", 200

@app.route('/login', methods=['POST', 'OPTIONS'])
def login_route():
    if request.method == 'OPTIONS':
        res = make_response('', 200)
        res.headers.add("Access-Control-Allow-Origin", "*")
        res.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        res.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return res

    # This MUST appear in your Render logs to prove the link works
    print("--> 🔔 CONNECTION RECEIVED FROM NETLIFY")
    
    try:
        data = request.get_json(silent=True) or {}
        game_id = data.get('game_id', 'orion')
        
        # This triggers the login_manager.py logic you provided earlier
        session = login_manager.perform_login(game_id)

        if session:
            return jsonify({"status": "success", "message": "Logged in"}), 200
        else:
            return jsonify({"status": "error", "message": "Login failed"}), 401
    except Exception as e:
        print(f"--> 💥 SYSTEM ERROR: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
