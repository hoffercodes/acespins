from flask import Flask, jsonify, request, make_response
from flask_cors import CORS 
import login_manager
import os

app = Flask(__name__)

# This allows your Vercel frontend to talk to this Render backend
CORS(app)

@app.after_request
def after_request(response):
    # These headers tell the browser "It is safe to talk to this backend"
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/login', methods=['POST', 'OPTIONS'])
def login_route():
    # Handle the browser's "pre-flight" test request
    if request.method == 'OPTIONS':
        return make_response('', 200)

    # THIS MUST PRINT IN YOUR RENDER LOGS IF THE CONNECTION IS GOOD
    print("--> 🔔 DOORBELL RANG: CONNECTION RECEIVED FROM FRONTEND")
    
    try:
        data = request.get_json(silent=True) or {}
        game_id = data.get('game_id', 'orion')
        
        # This calls the perform_login engine in login_manager.py
        session = login_manager.perform_login(game_id)

        if session:
            return jsonify({"status": "success", "message": f"Connected to {game_id}"}), 200
        else:
            return jsonify({"status": "error", "message": "Login failed"}), 401
    except Exception as e:
        print(f"--> 💥 ERROR: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
