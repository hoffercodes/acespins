from flask import Flask, jsonify, request
from flask_cors import CORS  # Import the fix
import login_manager
import os

app = Flask(__name__)

# 1. ENABLE CORS (Allow Vercel to talk to Render)
# This fixes the "Network Error" on the frontend
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Backend is Live! Use POST /login to start."

@app.route('/login', methods=['POST'])
def login_route():
    # 2. DEBUG PRINT (The Doorbell)
    # This proves the connection reached the server
    print("--> 🔔 RECEIVED LOGIN REQUEST FROM FRONTEND!")

    try:
        # Get data from frontend (if any)
        data = request.get_json(silent=True) or {}
        game_id = data.get('game_id', 'orion')

        print(f"--> Starting Login Process for: {game_id}")

        # Run the Login Manager (The code we just fixed)
        session = login_manager.perform_login(game_id)

        if session:
            # Login Success
            print("--> ✅ RETURNING SUCCESS TO FRONTEND")
            return jsonify({
                "status": "success", 
                "message": "Login Successful!", 
                "redirect": "Store.aspx"
            }), 200
        else:
            # Login Failed (Retries exhausted)
            print("--> ❌ RETURNING FAILURE TO FRONTEND")
            return jsonify({
                "status": "error", 
                "message": "Login Failed after multiple attempts."
            }), 401

    except Exception as e:
        print(f"--> 💥 CRITICAL SERVER ERROR: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
