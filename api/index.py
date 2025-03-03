from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import traceback
import sys

# This is a simplified handler for debugging
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = dict(urllib.parse.parse_qsl(parsed_path.query))
            
            # Return debug information
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ok",
                "path": path,
                "query_params": query_params,
                "headers": dict(self.headers),
                "serverless_info": {
                    "python_version": sys.version,
                    "platform": sys.platform
                }
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
            
        except Exception as e:
            # Capture the full error with traceback
            error_type = type(e).__name__
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            # Return detailed error information
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "error": error_type,
                "message": error_msg,
                "traceback": error_traceback,
                "path": self.path
            }
            
            self.wfile.write(json.dumps(error_response, indent=2).encode())
            return