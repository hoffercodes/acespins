from flask import Flask, jsonify, request
from flask_cors import CORS 
import login_manager
import os

app = Flask(__name__)

# 1. HARDENED CORS SETTINGS
# We are specifically allowing your Vercel frontend to talk to this backend.
CORS(app, resources={r"/*": {"origins": ["https://acespins.vercel.app", "http://localhost:3000"]}})

@app.route('/', methods=['GET'])
def home():
    return "Backend is Live! Use POST /login to start."

@app.route('/login', methods=['POST'])
def login_route():
    # THIS MUST SHOW UP IN LOGS IF CONNECTION IS GOOD
    print("--> 🔔 DOORBELL RANG: RECEIVED REQUEST FROM FRONTEND!")

    try:
        data = request.get_json(silent=True) or {}
        game_id = data.get('game_id', 'orion')
        print(f"--> User wants to log into: {game_id}")

        # Call the relay to login_manager.py
        session = login_manager.perform_login(game_id)

        if session:
            print("--> ✅ SUCCESS: Sending 200 OK back to Website")
            return jsonify({"status": "success", "message": "Logged in!"}), 200
        else:
            print("--> ❌ FAILURE: Sending 401 back to Website")
            return jsonify({"status": "error", "message": "Login failed"}), 401

    except Exception as e:
        print(f"--> 💥 ERROR: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
