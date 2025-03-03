from http.server import BaseHTTPRequestHandler
from flask import Flask, request, jsonify, Response
import urllib.parse
import io
import sys
import os

# Create Flask app
app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))

# Define Flask routes and functionality
@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return jsonify({
        "message": "Solana Wallet API is running",
        "instructions": "Use with Telegram Bot"
    })

# This is the handler class that Vercel expects
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Capture flask's response
        env = {
            'wsgi.input': io.BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'SERVER_SOFTWARE': 'Vercel',
            'REQUEST_METHOD': self.command,
            'PATH_INFO': self.path.split('?')[0],
            'QUERY_STRING': self.path.split('?')[1] if '?' in self.path else '',
            'SERVER_PROTOCOL': self.request_version,
            'wsgi.url_scheme': 'https'
        }
        
        # Add headers to the environment
        for header in self.headers:
            key = header.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = 'HTTP_' + key
            env[key] = self.headers[header]
            
        # Create a response container
        response_body = []
        
        def start_response(status, headers):
            self.send_response(int(status.split()[0]))
            for header, value in headers:
                self.send_header(header, value)
            self.end_headers()
            return response_body.append
            
        # Pass the request to Flask
        response = app(env, start_response)
        
        # Write the response
        for data in response:
            self.wfile.write(data)
            
        return