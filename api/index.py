from flask import Flask, request, jsonify, render_template_string
import secrets
import hashlib
import os
from datetime import datetime

# In-memory database (for demo only)
DB = {}

# Create Flask app
app = Flask(__name__)

# HTML templates as strings (since Vercel has issues with template directories)
WALLET_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Solana Wallet</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 16px;
            background-color: #1e1e2e;
            color: #ffffff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #2d2d3f;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .wallet-info {
            background-color: #3d3d5c;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .wallet-address {
            word-break: break-all;
            font-family: monospace;
            background-color: #2a2a40;
            padding: 12px;
            border-radius: 6px;
            font-size: 14px;
        }
        .balance {
            font-size: 28px;
            text-align: center;
            margin: 20px 0;
            color: #9ece6a;
        }
        .username {
            color: #bb9af7;
            font-weight: bold;
        }
        .label {
            color: #7aa2f7;
            margin-bottom: 6px;
            font-size: 14px;
        }
        .solana-logo {
            text-align: center;
            margin-bottom: 20px;
        }
        button {
            background-color: #7aa2f7;
            border: none;
            color: white;
            padding: 12px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 6px;
            width: 100%;
        }
        button:hover {
            background-color: #5d87e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="solana-logo">
                <svg width="126" height="22" viewBox="0 0 126 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4.20106 4.1693H19.6454C20.0025 4.1693 20.1805 4.60466 19.9262 4.8568L15.5639 9.18182H4.20106C3.91452 9.18182 3.68406 8.9534 3.68406 8.67011V4.67577C3.68406 4.39248 3.91452 4.1693 4.20106 4.1693Z" fill="#9945FF"/>
                    <path d="M4.20106 17.8307H19.6454C20.0025 17.8307 20.1805 17.3953 19.9262 17.1432L15.5639 12.8182H4.20106C3.91452 12.8182 3.68406 13.0466 3.68406 13.3299V17.3242C3.68406 17.6075 3.91452 17.8307 4.20106 17.8307Z" fill="#14F195"/>
                    <path d="M15.563 9.18182L19.9254 13.5068C20.1796 13.759 19.9967 14.1944 19.6445 14.1944H4.20106C3.91452 14.1944 3.68406 13.966 3.68406 13.6827V9.68835C3.68406 9.40506 3.91452 9.18182 4.20106 9.18182H15.563Z" fill="#00C2FF"/>
                </svg>
            </div>
            <h1>Your Solana Wallet</h1>
            <p>Welcome, <span class="username">@{{ username }}</span>!</p>
        </div>
        
        <div class="wallet-info">
            <div class="label">Your Wallet Address:</div>
            <div class="wallet-address">{{ wallet_address }}</div>
            
            <div class="balance">
                {{ balance }} SOL
            </div>
        </div>
        
        <button id="closeButton">Close</button>
    </div>

    <script>
        // Initialize Telegram WebApp
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        // Close button handler
        document.getElementById('closeButton').addEventListener('click', function() {
            tg.close();
        });
        
        // Notify Telegram WebApp when the page is fully loaded
        window.addEventListener('load', function() {
            tg.ready();
        });
    </script>
</body>
</html>
'''

ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 16px;
            background-color: #1e1e2e;
            color: #ffffff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #2d2d3f;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        .error-icon {
            font-size: 64px;
            margin-bottom: 20px;
            color: #f7768e;
        }
        .error-message {
            margin-bottom: 30px;
        }
        button {
            background-color: #7aa2f7;
            border: none;
            color: white;
            padding: 12px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 6px;
            width: 100%;
        }
        button:hover {
            background-color: #5d87e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">⚠️</div>
        <h1>Error</h1>
        <div class="error-message">{{ message }}</div>
        <button id="closeButton">Close</button>
    </div>

    <script>
        // Initialize Telegram WebApp
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        // Close button handler
        document.getElementById('closeButton').addEventListener('click', function() {
            tg.close();
        });
        
        // Notify Telegram WebApp when the page is fully loaded
        window.addEventListener('load', function() {
            tg.ready();
        });
    </script>
</body>
</html>
'''

# Simple Solana wallet creation
def create_solana_wallet():
    """
    Creates a simple Solana wallet with a keypair.
    """
    # Generate a random private key
    private_key = secrets.token_bytes(32)
    private_key_hex = private_key.hex()
    
    # For demo purposes, derive a public key from the private key
    public_key = "So" + hashlib.sha256(private_key).hexdigest()[:32]
    
    return public_key, private_key_hex

# Get Solana balance from public API
def get_solana_balance(public_key):
    """
    Fetches a wallet's SOL balance.
    """
    # For demo, return a fixed value
    return 0.05  # 0.05 SOL

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    try:
        # Log request info (helpful for debugging)
        print(f"Request received: {request.url}")
        print(f"Query parameters: {request.args}")
        
        # Get user parameters from query string
        telegram_id = request.args.get('id')
        telegram_username = request.args.get('username', '')
        
        if not telegram_id:
            return render_template_string(ERROR_TEMPLATE, message="No user ID provided")
        
        # Check if user exists in database
        user = DB.get(telegram_id)
        
        # If user doesn't exist, create wallet and add to database
        if not user:
            public_key, private_key = create_solana_wallet()
            
            user = {
                'telegram_id': telegram_id,
                'telegram_username': telegram_username,
                'wallet_public_key': public_key,
                'wallet_private_key': private_key,
                'created_at': datetime.now().isoformat()
            }
            DB[telegram_id] = user
            print(f"Created new wallet for user {telegram_id}")
        else:
            print(f"Retrieved existing wallet for user {telegram_id}")
        
        # Get wallet balance
        balance = get_solana_balance(user['wallet_public_key'])
        
        # Render template with user data
        return render_template_string(
            WALLET_TEMPLATE, 
            username=telegram_username or "User",
            wallet_address=user['wallet_public_key'],
            balance=balance
        )
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template_string(ERROR_TEMPLATE, message=f"Error: {str(e)}")

# Simple health check endpoint
@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

# For local development
if __name__ == '__main__':
    app.run(debug=True)