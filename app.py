# app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import login_manager
import data_fetcher
import action_handler
import config
import os

app = Flask(__name__)

# IMPORTANT: This allows your Vercel frontend to talk to this Render backend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Global dictionary to keep your game sessions alive
sessions = {}

@app.route('/')
def index():
    """
    Serves your frontend from the 'templates' folder.
    Note: Flask looks specifically for a folder named 'templates'.
    """
    return render_template('index.html') 

@app.route('/api/connect', methods=['POST'])
def connect():
    """
    Triggers the automatic login loop in login_manager.py.
    This will stay 'pending' until the captcha is solved.
    """
    data = request.json
    game_id = data.get('game_id', 'orion')
    try:
        # Calls your looping login_manager.py
        session = login_manager.perform_login()
        if session:
            sessions[game_id] = session
            return jsonify({
                "status": "success", 
                "message": f"{game_id.capitalize()} Connected Successfully!"
            })
        return jsonify({"status": "error", "message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401

@app.route('/api/search', methods=['POST'])
def search():
    """
    Searches for a player using the active session.
    """
    data = request.json
    game_id = data.get('game_id', 'orion')
    query = data.get('query')

    if game_id not in sessions:
        return jsonify({"error": "Session expired. Please reconnect."}), 401
    
    user = data_fetcher.search_user(sessions[game_id], query)
    return jsonify(user) if user else jsonify({"error": "User not found"})

@app.route('/api/action', methods=['POST'])
def handle_action():
    """
    Routes actions (recharge, redeem, etc.) to the action_handler.py.
    """
    data = request.json
    game_id = data.get('game_id', 'orion')
    session = sessions.get(game_id)
    
    if not session: 
        return jsonify({"error": "No active session found"}), 401

    act = data['action']
    user_data = data.get('user')
    amount = data.get('amount')

    try:
        if act == "create_player":
            res = action_handler.create_new_player(
                session, data['username'], data['password'], data.get('nickname')
            )
        elif act == "recharge":
            res = action_handler.recharge(session, user_data, amount)
        elif act == "redeem":
            res = action_handler.redeem(session, user_data, amount)
        elif act == "ban":
            res = action_handler.ban_unban(session, user_data)
        elif act == "unbind":
            res = action_handler.unbind_device(session, user_data)
        else:
            return jsonify({"error": "Invalid action"}), 400
            
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Use port 5000 for local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
