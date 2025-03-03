from flask import Flask, request, render_template, jsonify, Response
import sqlite3
import os
import secrets
import hashlib
import json

# HTML template for wallet display when templates are not accessible
WALLET_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Your Solana Wallet</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 16px;
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
        <div class="error-message">{message}</div>
        <button id="closeButton">Close</button>
    </div>

    <script>
        // Initialize Telegram WebApp
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        
        // Close button handler
        document.getElementById('closeButton').addEventListener('click', function() {
            tg.close();
        });
    </script>
</body>
</html>"""

app = Flask(__name__, template_folder="../templates")1e1e2e;
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
                    <path d="M35.25 7.64999V16.7H33.2V9.69999H30.75V7.64999H35.25ZM41.5434 9.34999C42.4634 9.34999 43.1934 9.64999 43.7334 10.25C44.2734 10.84 44.5434 11.64 44.5434 12.65V16.7H42.5434V12.95C42.5434 12.39 42.4034 11.96 42.1234 11.65C41.8434 11.33 41.4534 11.17 40.9534 11.17C40.4034 11.17 39.9634 11.34 39.6334 11.68C39.3134 12.02 39.1534 12.51 39.1534 13.15V16.7H37.1534V9.44999H39.1534V10.28C39.4134 9.99999 39.7334 9.77999 40.1134 9.61999C40.5034 9.43999 40.9934 9.34999 41.5434 9.34999ZM50.2775 9.34999C51.3475 9.34999 52.2175 9.69999 52.8875 10.4C53.5675 11.09 53.9075 12.01 53.9075 13.15C53.9075 14.29 53.5675 15.21 52.8875 15.91C52.2175 16.61 51.3475 16.96 50.2775 16.96C49.1775 16.96 48.2975 16.59 47.6375 15.85V19.73H45.6375V9.44999H47.6375V10.45C48.2975 9.71999 49.1775 9.34999 50.2775 9.34999ZM49.8575 15.22C50.4075 15.22 50.8575 15.03 51.2075 14.65C51.5675 14.26 51.7475 13.75 51.7475 13.12C51.7475 12.49 51.5675 11.98 51.2075 11.6C50.8575 11.21 50.4075 11.02 49.8575 11.02C49.3075 11.02 48.8575 11.21 48.5075 11.59C48.1575 11.97 47.9775 12.48 47.9775 13.12C47.9775 13.76 48.1575 14.27 48.5075 14.65C48.8575 15.03 49.3075 15.22 49.8575 15.22ZM65.3195 12.93C65.3195 13.03 65.3095 13.19 65.2895 13.41H58.9795C59.0695 13.93 59.2995 14.34 59.6695 14.64C60.0395 14.94 60.4995 15.09 61.0495 15.09C61.4495 15.09 61.7995 15.02 62.0995 14.88C62.4095 14.73 62.6695 14.51 62.8795 14.22L64.5295 15.33C63.8595 16.42 62.6995 16.96 61.0495 16.96C59.8595 16.96 58.8895 16.6 58.1395 15.88C57.3895 15.15 57.0195 14.22 57.0195 13.09C57.0195 11.97 57.3895 11.05 58.1295 10.33C58.8695 9.60998 59.8195 9.24999 60.9795 9.24999C62.0795 9.24999 62.9795 9.60998 63.6795 10.33C64.3795 11.05 64.7295 11.98 64.7295 13.12C64.7295 13.32 64.7195 13.57 64.6995 13.87L65.3195 12.93ZM60.9895 11.01C60.4995 11.01 60.0895 11.15 59.7695 11.43C59.4495 11.71 59.2395 12.09 59.1495 12.57H62.8295C62.7395 12.1 62.5295 11.72 62.1995 11.44C61.8795 11.15 61.4795 11.01 60.9895 11.01ZM71.5975 9.34999C72.5175 9.34999 73.2475 9.64999 73.7875 10.25C74.3275 10.84 74.5975 11.64 74.5975 12.65V16.7H72.5975V12.95C72.5975 12.39 72.4575 11.96 72.1775 11.65C71.8975 11.33 71.5075 11.17 71.0075 11.17C70.4575 11.17 70.0175 11.34 69.6875 11.68C69.3675 12.02 69.2075 12.51 69.2075 13.15V16.7H67.2075V6.14999H69.2075V10.28C69.4675 9.99999 69.7875 9.77999 70.1675 9.61999C70.5575 9.43999 71.0475 9.34999 71.5975 9.34999ZM85.2503 12.93C85.2503 13.03 85.2402 13.19 85.2203 13.41H78.9103C79.0003 13.93 79.2303 14.34 79.6003 14.64C79.9703 14.94 80.4303 15.09 80.9803 15.09C81.3803 15.09 81.7303 15.02 82.0303 14.88C82.3403 14.73 82.6003 14.51 82.8103 14.22L84.4603 15.33C83.7903 16.42 82.6303 16.96 80.9803 16.96C79.7903 16.96 78.8202 16.6 78.0703 15.88C77.3203 15.15 76.9503 14.22 76.9503 13.09C76.9503 11.97 77.3203 11.05 78.0603 10.33C78.8003 9.60998 79.7502 9.24999 80.9103 9.24999C82.0103 9.24999 82.9103 9.60998 83.6103 10.33C84.3103 11.05 84.6603 11.98 84.6603 13.12C84.6603 13.32 84.6503 13.57 84.6303 13.87L85.2503 12.93ZM80.9203 11.01C80.4303 11.01 80.0203 11.15 79.7003 11.43C79.3803 11.71 79.1703 12.09 79.0803 12.57H82.7603C82.6703 12.1 82.4602 11.72 82.1303 11.44C81.8103 11.15 81.4103 11.01 80.9203 11.01Z" fill="white"/>
                </svg>
            </div>
            <h1>Your Solana Wallet</h1>
            <p>Welcome, <span class="username">@{username}</span>!</p>
        </div>
        
        <div class="wallet-info">
            <div>Your Wallet Address:</div>
            <div class="wallet-address">{wallet_address}</div>
            
            <div class="balance">
                {balance} SOL
            </div>
        </div>
        
        <button id="closeButton">Close</button>
    </div>

    <script>
        // Initialize Telegram WebApp
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        
        // Close button handler
        document.getElementById('closeButton').addEventListener('click', function() {
            tg.close();
        });
    </script>
</body>
</html>"""

# Error HTML template
ERROR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
            background-color: #

# Database setup
def get_db_connection():
    conn = sqlite3.connect('/tmp/telegram_solana.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        telegram_username TEXT,
        wallet_public_key TEXT,
        wallet_private_key TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Simple Solana wallet creation
def create_solana_wallet():
    private_key = secrets.token_bytes(32)
    private_key_hex = private_key.hex()
    public_key = "So" + hashlib.sha256(private_key).hexdigest()[:32]
    return public_key, private_key_hex

# Get Solana balance from public API
def get_solana_balance(public_key):
    return 0.05  # Demo value

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Get user parameters from query string
    telegram_id = request.args.get('id')
    telegram_username = request.args.get('username', '')
    
    if not telegram_id:
        return render_template('error.html', message="No user ID provided")
    
    try:
        # Check if user exists in database
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE telegram_id = ?', 
                          (telegram_id,)).fetchone()
        
        # If user doesn't exist, create wallet and add to database
        if not user:
            public_key, private_key = create_solana_wallet()
            
            conn.execute(
                'INSERT INTO users (telegram_id, telegram_username, wallet_public_key, wallet_private_key) VALUES (?, ?, ?, ?)',
                (telegram_id, telegram_username, public_key, private_key)
            )
            conn.commit()
            
            # Fetch the newly created user
            user = conn.execute('SELECT * FROM users WHERE telegram_id = ?', 
                              (telegram_id,)).fetchone()
        
        # Get wallet balance
        balance = get_solana_balance(user['wallet_public_key'])
        
        conn.close()
        
        # Render template with user data
        return render_template('wallet.html', 
                               username=telegram_username or "User",
                               wallet_address=user['wallet_public_key'],
                               balance=balance)
    
    except Exception as e:
        return render_template('error.html', message=f"Error: {str(e)}")

# Vercel serverless function handler
def handler(event, context):
    """Adapter for Vercel Serverless"""
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)