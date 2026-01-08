from flask import Flask, jsonify, request
from flask_cors import CORS
import login_manager
import data_fetcher
import action_handler
import os
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# GLOBAL SESSION STORAGE (Keeps the bot logged in!)
active_session = None
last_login_time = 0

@app.route('/')
def home():
    return "Backend is Live & Fast!"

@app.route('/api/connect', methods=['POST', 'OPTIONS'])
def connect():
    global active_session, last_login_time
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    # 1. INSTANT CHECK: Are we already logged in?
    # If less than 10 minutes passed, reuse the old session!
    if active_session and (time.time() - last_login_time < 600):
        print("⚡ Using CACHED Session (Fast Login)")
        return jsonify({"success": True, "message": "Instant Login"}), 200

    # 2. SLOW LOGIN (Only happens once every 10 mins)
    try:
        data = request.json
        game_id = data.get('game_id', 'orion')
        session = login_manager.perform_login(game_id)
        
        if session:
            active_session = session # Save it!
            last_login_time = time.time()
            return jsonify({"success": True, "message": "Fresh Login"}), 200
        
        return jsonify({"success": False, "message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ... (Keep search and action routes the same) ...
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
