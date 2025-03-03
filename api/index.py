from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import base64
import secrets
import hashlib
import requests

app = Flask(__name__)

# Database setup
def get_db_connection():
    conn = sqlite3.connect('/tmp/telegram_solana.db')  # Use /tmp for Vercel
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
    """
    Creates a simple Solana wallet with a keypair.
    In a production environment, you'd use the actual Solana SDK.
    """
    # Generate a random private key
    private_key = secrets.token_bytes(32)
    private_key_hex = private_key.hex()
    
    # For demo purposes, derive a public key from the private key
    # In a real implementation, you'd use proper ED25519 key derivation
    public_key = "So" + hashlib.sha256(private_key).hexdigest()[:32]
    
    return public_key, private_key_hex

# Get Solana balance from public API
def get_solana_balance(public_key):
    """
    Fetches a wallet's SOL balance.
    For demo purposes, we'll just return a fixed value.
    In production, you'd query the Solana blockchain.
    """
    try:
        # In a real app, you'd use something like:
        # response = requests.get(f"https://api.devnet.solana.com", 
        #                        json={"jsonrpc":"2.0", "id":1, "method":"getBalance", "params":[public_key]})
        # return response.json()['result']['value'] / 1_000_000_000  # Convert lamports to SOL
        
        # For demo, return a fixed value
        return 0.05  # 0.05 SOL
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
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