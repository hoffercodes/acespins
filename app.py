# app.py
from flask import Flask, request, jsonify
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
    Since Frontend is on Vercel, we don't serve index.html here anymore.
    We just return a simple message to show the Backend is running.
    """
    return "Acespins Backend is Running. Frontend is hosted on Vercel."

@app.route('/api/connect', methods=['POST'])
def connect():
    data = request.json
    game_id = data.get('game_id', 'orion')
    try:
        # Pass game_id to login manager if your script supports multiple games
        session = login_manager.perform_login(game_id) if hasattr(login_manager, 'perform_login') and login_manager.perform_login.__code__.co_argcount > 0 else login_manager.perform_login()
        
        if session:
            sessions[game_id] = session
            # Updated to "success: True" to match your React Frontend
            return jsonify({
                "success": True, 
                "message": f"{game_id.capitalize()} Connected Successfully!"
            })
        return jsonify({"success": False, "message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 401

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    game_id = data.get('game_id', 'orion')
    query = data.get('query')

    if game_id not in sessions:
        return jsonify({"success": False, "message": "Session expired. Please reconnect."}), 401
    
    user = data_fetcher.search_user(sessions[game_id], query)
    
    if user:
        user['success'] = True # Add success flag for frontend
        return jsonify(user)
    else:
        return jsonify({"success": False, "message": "User not found"})

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    game_id = data.get('game_id', 'orion')
    session = sessions.get(game_id)
    
    if not session: 
        return jsonify({"success": False, "message": "No active session found"}), 401

    act = data.get('action')
    user_data = data.get('user')
    amount = data.get('amount')

    try:
        if act == "create_player":
            # Updated to match the new React frontend data structure
            res = action_handler.create_new_player(
                session, data.get('username'), data.get('password'), data.get('nickname')
            )
        elif act == "recharge":
            res = action_handler.recharge(session, user_data, amount)
        elif act == "redeem":
            res = action_handler.redeem(session, user_data, amount)
        elif act == "ban":
            res = action_handler.ban_unban(session, user_data)
        elif act == "unbind":
            res = action_handler.unbind_device(session, user_data)
        elif act == "resetpass":
             # Handle password reset if needed
             new_pass = data.get('password')
             res = action_handler.reset_password(session, user_data, new_pass)
        else:
            return jsonify({"success": False, "message": "Invalid action"}), 400
            
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    
