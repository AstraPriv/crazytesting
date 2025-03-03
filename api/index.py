from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import base64
import secrets
import hashlib
import requests

# Updated to properly handle template paths in Vercel
app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))

# Database setup with better error handling
def get_db_connection():
    try:
        conn = sqlite3.connect('/tmp/telegram_solana.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        # Create a backup connection if the primary fails
        return sqlite3.connect(':memory:')

def init_db():
    try:
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
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# Initialize database
db_init_status = init_db()

# Simple Solana wallet creation with error handling
def create_solana_wallet():
    try:
        # Generate a random private key
        private_key = secrets.token_bytes(32)
        private_key_hex = private_key.hex()
        
        # For demo purposes, derive a public key from the private key
        # In a real implementation, you'd use proper ED25519 key derivation
        public_key = "So" + hashlib.sha256(private_key).hexdigest()[:32]
        
        return public_key, private_key_hex
    except Exception as e:
        print(f"Wallet creation error: {e}")
        # Return a placeholder wallet in case of error
        return "SoERROR", "ERROR"

# Get Solana balance from public API with improved error handling
def get_solana_balance(public_key):
    try:
        # For demo, return a fixed value
        return 0.05  # 0.05 SOL
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0

# Define a health check route
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "db_initialized": db_init_status
    })

# Main route handler with better error handling
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    try:
        # Get user parameters from query string
        telegram_id = request.args.get('id')
        telegram_username = request.args.get('username', '')
        
        if not telegram_id:
            return render_template('error.html', message="No user ID provided")
        
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
        # Detailed error handling for debugging
        error_details = str(e)
        print(f"Handler error: {error_details}")
        return render_template('error.html', message=f"Error: {error_details}")

# Add this to enable local testing
if __name__ == '__main__':
    app.run(debug=True)