from flask import Flask, jsonify, request, make_response
from flask_cors import CORS 
import login_manager
import os

app = Flask(__name__)

# Nuclear CORS: This allows your Netlify site to talk to Render
CORS(app, supports_credentials=True)

@app.route('/', methods=['GET'])
def home():
    # This prevents the "Not Found" error you saw
    return "AceSpins Backend is Active!", 200

@app.route('/login', methods=['POST', 'OPTIONS'])
def login_route():
    if request.method == 'OPTIONS':
        res = make_response('', 200)
        res.headers.add("Access-Control-Allow-Origin", "*")
        res.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        res.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return res

    # THIS LOG MUST APPEAR IN RENDER LOGS
    print("--> 🔔 CONNECTION RECEIVED FROM NETLIFY")
    
    try:
        data = request.get_json(silent=True) or {}
        game_id = data.get('game_id', 'orion')
        
        # Trigger the logic in login_manager.py
        session = login_manager.perform_login(game_id)

        if session:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Login failed"}), 401
    except Exception as e:
        print(f"--> 💥 ERROR: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
