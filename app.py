from flask import Flask, jsonify, request
from flask_cors import CORS
import login_manager
import data_fetcher
import action_handler
import os

app = Flask(__name__)

# Allow Vercel to talk to this backend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Store active sessions
sessions = {}

@app.route('/')
def home():
    return "Backend is running. Frontend is on Vercel."

@app.route('/api/connect', methods=['POST'])
def connect():
    data = request.json
    game_id = data.get('game_id', 'orion')
    try:
        # Attempt login
        session = login_manager.perform_login(game_id) if hasattr(login_manager, 'perform_login') and login_manager.perform_login.__code__.co_argcount > 0 else login_manager.perform_login()

        if session:
            sessions[game_id] = session
            return jsonify({"success": True, "message": f"{game_id.capitalize()} Connected!"})
        return jsonify({"success": False, "message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    game_id = data.get('game_id', 'orion')
    query = data.get('query')
    session = sessions.get(game_id)

    if not session:
        return jsonify({"success": False, "message": "Session expired."}), 401

    user = data_fetcher.search_user(session, query)
    if user:
        user['success'] = True
        return jsonify(user)
    return jsonify({"success": False, "message": "User not found"})

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    game_id = data.get('game_id', 'orion')
    session = sessions.get(game_id)

    if not session: 
        return jsonify({"success": False, "message": "Session expired."}), 401

    act = data.get('action')
    try:
        if act == "create_player":
            res = action_handler.create_new_player(session, data.get('username'), data.get('password'), data.get('nickname'))
        elif act == "recharge":
            res = action_handler.recharge(session, data.get('user'), data.get('amount'))
        elif act == "redeem":
            res = action_handler.redeem(session, data.get('user'), data.get('amount'))
        elif act == "ban":
            res = action_handler.ban_unban(session, data.get('user'))
        elif act == "unbind":
            res = action_handler.unbind_device(session, data.get('user'))
        elif act == "resetpass":
            res = action_handler.reset_password(session, data.get('user'), data.get('password'))
        else:
            return jsonify({"success": False, "message": "Invalid action"}), 400

        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
