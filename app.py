# app.py
from flask import Flask, render_template, request, jsonify
import login_manager
import data_fetcher
import action_handler
import config

app = Flask(__name__)

# Global dictionary to keep your game sessions alive
sessions = {}

@app.route('/') # FIXED: This makes it the main page
def index():
    # FIXED: Changed from dashboard.html to index.html to match your GitHub file
    return render_template('index.html') 

@app.route('/api/connect', methods=['POST'])
def connect():
    game_id = request.json.get('game_id')
    try:
        # Calls your looping login_manager.py
        session = login_manager.perform_login()
        if session:
            sessions[game_id] = session
            return jsonify({"status": "success", "message": f"{game_id} Connected!"})
        return jsonify({"status": "error", "message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    game_id = data.get('game_id')
    if game_id not in sessions:
        return jsonify({"error": "Session expired"}), 401
    
    user = data_fetcher.search_user(sessions[game_id], data['query'])
    return jsonify(user) if user else jsonify({"error": "User not found"})

@app.route('/api/action', methods=['POST'])
def handle_action():
    data = request.json
    game_id = data.get('game_id')
    session = sessions.get(game_id)
    if not session: return jsonify({"error": "No Session"}), 401

    act = data['action']
    if act == "create_player":
        res = action_handler.create_new_player(session, data['username'], data['password'], data.get('nickname'))
    elif act == "recharge":
        res = action_handler.recharge(session, data['user'], data['amount'])
    elif act == "redeem":
        res = action_handler.redeem(session, data['user'], data['amount'])
    elif act == "ban":
        res = action_handler.ban_unban(session, data['user'])
    elif act == "unbind":
        res = action_handler.unbind_device(session, data['user'])
    
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
