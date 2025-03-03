from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import traceback
import sqlite3
import os
import secrets
import hashlib

# Simple HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
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
</html>"""

ERROR_HTML_TEMPLATE = """<!DOCTYPE html>
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
        <div class="error-message">{message}</div>
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
</html>"""

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
    return True

# Simple Solana wallet creation
def create_solana_wallet():
    private_key = secrets.token_bytes(32)
    private_key_hex = private_key.hex()
    public_key = "So" + hashlib.sha256(private_key).hexdigest()[:32]
    return public_key, private_key_hex

# Get Solana balance from public API
def get_solana_balance(public_key):
    return 0.05  # Demo value

# Initialize database
init_db()

# Handler class
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse the URL and query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = dict(urllib.parse.parse_qsl(parsed_path.query))
            
            # Debug endpoint - returns JSON data
            if path == '/api/debug':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "ok",
                    "message": "Handler is working",
                    "query_params": query_params
                }).encode())
                return
            
            # Main endpoint - returns HTML
            telegram_id = query_params.get('id')
            telegram_username = query_params.get('username', 'User')
            
            # If no ID provided, return error HTML
            if not telegram_id:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_content = ERROR_HTML_TEMPLATE.format(message="No user ID provided")
                self.wfile.write(error_content.encode())
                return
            
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
            
            # Return HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            wallet_content = HTML_TEMPLATE.format(
                username=telegram_username,
                wallet_address=user['wallet_public_key'],
                balance=balance
            )
            
            self.wfile.write(wallet_content.encode())
            return
                
        except Exception as e:
            # Return error information
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_content = ERROR_HTML_TEMPLATE.format(message=f"Error: {str(e)}")
            self.wfile.write(error_content.encode())
            return