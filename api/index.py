from flask import Flask, request, jsonify, render_template
import os
import sqlite3
import secrets
import hashlib

# Initialize Flask app at module level - THIS IS CRITICAL FOR VERCEL
app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))

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

# Simple Solana wallet creation
def create_solana_wallet():
    private_key = secrets.token_bytes(32)
    private_key_hex = private_key.hex()
    public_key = "So" + hashlib.sha256(private_key).hexdigest()[:32]
    return public_key, private_key_hex

# Get Solana balance
def get_solana_balance(public_key):
    return 0.05  # Demo value

# Initialize database at module level
init_db()

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

# Main route handler
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
        return render_template('error.html', message=f"Error: {str(e)}")

# This is required for Vercel - DO NOT REMOVE
if __name__ == '__main__':
    app.run(debug=True)