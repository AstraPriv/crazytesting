from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import traceback
import sqlite3
import os
import secrets
import hashlib

# Define fixed-length error templates to ensure they don't cause issues
ERROR_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>
        body { font-family: Arial; background: #1e1e2e; color: white; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; background: #2d2d3f; border-radius: 12px; }
        pre { white-space: pre-wrap; word-wrap: break-word; background: #1a1a2e; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Error Details</h1>
        <h3>Error Type: {error_type}</h3>
        <h3>Error Message:</h3>
        <pre>{error_msg}</pre>
        <h3>Stack Trace:</h3>
        <pre>{traceback}</pre>
        <h3>Step:</h3>
        <pre>{step}</pre>
        <h3>Details:</h3>
        <pre>{details}</pre>
    </div>
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
        current_step = "initialization"
        details = {}
        
        try:
            # Parse the URL and query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = dict(urllib.parse.parse_qsl(parsed_path.query))
            details["query_params"] = query_params
            
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
            
            # Step 1: Get telegram ID
            current_step = "getting telegram ID"
            telegram_id = query_params.get('id')
            telegram_username = query_params.get('username', 'User')
            details["telegram_id"] = telegram_id
            details["telegram_username"] = telegram_username
            
            # If no ID provided, return simple error
            if not telegram_id:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("Error: No user ID provided".encode())
                return
                
            # Step 2: Connect to database
            current_step = "connecting to database"
            conn = get_db_connection()
            
            # Step 3: Check if user exists in database
            current_step = "checking if user exists"
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
            user_result = cursor.fetchone()
            
            # Detailed logging of what we found
            if user_result:
                details["user_exists"] = True
                # Convert row to dict for debugging
                user_dict = {}
                for key in user_result.keys():
                    user_dict[key] = user_result[key]
                details["user_data"] = user_dict
            else:
                details["user_exists"] = False
            
            # Step 4: Create wallet if user doesn't exist
            current_step = "creating wallet if needed"
            if not user_result:
                public_key, private_key = create_solana_wallet()
                details["generated_public_key"] = public_key
                details["generated_private_key"] = private_key[:5] + "..." # Show just beginning
                
                cursor.execute(
                    'INSERT INTO users (telegram_id, telegram_username, wallet_public_key, wallet_private_key) VALUES (?, ?, ?, ?)',
                    (telegram_id, telegram_username, public_key, private_key)
                )
                conn.commit()
                
                # Fetch the newly created user
                cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
                user_result = cursor.fetchone()
                
                # Log what we inserted
                if user_result:
                    user_dict = {}
                    for key in user_result.keys():
                        user_dict[key] = user_result[key]
                    details["inserted_user_data"] = user_dict
            
            # Step 5: Get wallet balance
            current_step = "getting wallet balance"
            balance = get_solana_balance(user_result['wallet_public_key'])
            details["balance"] = balance
            
            # Step 6: Prepare data for template
            current_step = "preparing template data"
            template_data = {
                "username": telegram_username,
                "wallet_address": user_result['wallet_public_key'],
                "balance": balance
            }
            details["template_data"] = template_data
            
            # Step 7: Close database connection
            current_step = "closing database connection"
            conn.close()
            
            # Step 8: Return JSON with all the processed data (for debugging)
            current_step = "returning JSON response"
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Return all processing details and template data
            response = {
                "status": "success",
                "processing_steps": details,
                "template_data": template_data
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
                
        except Exception as e:
            # Return detailed error information
            error_type = type(e).__name__
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Format the detailed error page
            error_content = ERROR_HTML_TEMPLATE.format(
                error_type=error_type,
                error_msg=error_msg,
                traceback=error_traceback,
                step=current_step,
                details=json.dumps(details, indent=2)
            )
            
            self.wfile.write(error_content.encode())
            return