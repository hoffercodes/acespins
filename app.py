from flask import Flask, jsonify, request, make_response
from flask_cors import CORS 
import login_manager
import data_fetcher  # NEW: Import your data fetcher
import os

app = Flask(__name__)
CORS(app)

# We need a global variable or a way to store the session after login
# For a simple version, we'll use a global, but for multi-user, we'd use a store
active_session = None 

@app.route('/', methods=['GET'])
def home():
    return "AceSpins Multi-Backend Engine: Active", 200

@app.route('/login', methods=['POST'])
def login_route():
    global active_session
    print("--> 🔔 LOGIN REQUEST RECEIVED")
    try:
        data = request.get_json(silent=True) or {}
        game_id = data.get('game_id', 'orion')
        
        # Trigger your login engine
        session = login_manager.perform_login(game_id)

        if session:
            active_session = session # Save session for searching later
            print("--> ✅ SESSION SAVED")
            return jsonify({"status": "success", "message": "Logged in"}), 200
        else:
            return jsonify({"status": "error", "message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/search', methods=['POST'])
def search_route():
    global active_session
    print("--> 🔍 SEARCH REQUEST RECEIVED")
    
    if not active_session:
        print("--> ❌ NO ACTIVE SESSION. LOG IN FIRST.")
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        data = request.get_json(silent=True) or {}
        target_name = data.get('query') # This matches your api.ts 'query'
        
        # Call your data_fetcher.py function
        player_data = data_fetcher.search_user(active_session, target_name)
        
        if player_data:
            print(f"--> ✅ FOUND PLAYER: {player_data['username']}")
            return jsonify(player_data), 200
        else:
            print("--> ❌ PLAYER NOT FOUND")
            return jsonify({"status": "error", "message": "User not found"}), 404
            
    except Exception as e:
        print(f"--> 💥 SEARCH ERROR: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
