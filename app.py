from flask import Flask, jsonify, request
from flask_cors import CORS 
import login_manager
import os

app = Flask(__name__)

# Allow your unified management portal to talk to this backend
CORS(app, resources={r"/*": {"origins": ["https://acespins.vercel.app"]}})

@app.route('/login', methods=['POST', 'OPTIONS'])
def login_route():
    # If the connection is fixed, this MUST appear in logs
    print("--> 🔔 DOORBELL RANG: REQUEST RECEIVED FROM MANAGEMENT SUITE")
    
    try:
        data = request.get_json(silent=True) or {}
        game_id = data.get('game_id', 'orion')
        
        # This calls the perform_login function you just shared
        session = login_manager.perform_login(game_id)

        if session:
            return jsonify({"status": "success", "message": f"Connected to {game_id}"}), 200
        else:
            return jsonify({"status": "error", "message": "Login failed"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
