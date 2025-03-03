from flask import Flask, request, render_template, jsonify, Response
import sqlite3
import os
import base64
import secrets
import hashlib
import json
from datetime import datetime

app = Flask(__name__)

# Initialize database (in-memory for Vercel)
DB = {}

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
        # For demo, return a fixed value
        return 0.05  # 0.05 SOL
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0

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
        
        # Get wallet balance
        balance = get_solana_balance(user['wallet_public_key'])
        
        # Render template with user data
        return render_template('wallet.html', 
                               username=telegram_username or "User",
                               wallet_address=user['wallet_public_key'],
                               balance=balance)
    
    except Exception as e:
        return render_template('error.html', message=f"Error: {str(e)}")

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)