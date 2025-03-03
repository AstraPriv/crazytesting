from flask import Flask, jsonify

# Create a minimal Flask app
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    # Return a simple JSON response to verify function works
    return jsonify({
        "status": "ok",
        "message": "Flask app is running",
        "path": path,
        "query_params": dict(request.args)
    })

# This is required for Vercel to properly identify the entry point
from flask import request