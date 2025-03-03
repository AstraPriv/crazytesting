from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import traceback
import sys
import os
import sqlite3

# Database functions with detailed error reporting
def get_db_connection():
    try:
        # Try connecting to SQLite database in /tmp
        conn = sqlite3.connect('/tmp/telegram_solana.db')
        conn.row_factory = sqlite3.Row
        return conn, None
    except Exception as e:
        error_details = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        return None, error_details

def init_db():
    try:
        conn, error = get_db_connection()
        if error:
            return False, error
            
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
        return True, None
    except Exception as e:
        error_details = {
            "message": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        return False, error_details

# Handler class
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = dict(urllib.parse.parse_qsl(parsed_path.query))
            
            # Try database initialization
            db_init_success, db_init_error = init_db()
            
            # Try basic database query
            db_query_result = None
            db_query_error = None
            
            if db_init_success:
                try:
                    conn, _ = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    db_query_result = [dict(table) for table in tables]
                    conn.close()
                except Exception as e:
                    db_query_error = {
                        "message": str(e),
                        "type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
            
            # Return debug information
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ok",
                "path": path,
                "query_params": query_params,
                "database": {
                    "initialization": {
                        "success": db_init_success,
                        "error": db_init_error
                    },
                    "query": {
                        "success": db_query_result is not None,
                        "result": db_query_result,
                        "error": db_query_error
                    }
                },
                "env": {
                    "temp_dir": os.environ.get('TEMP', 'Not set'),
                    "tmp_dir": os.environ.get('TMP', 'Not set'),
                    "tmpdir": os.environ.get('TMPDIR', 'Not set'),
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "writable_dirs": self._find_writable_dirs()
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
    
    def _find_writable_dirs(self):
        """Try to find directories that are writable in the environment"""
        test_dirs = ['/tmp', '/var/task', '.', '/var/task/tmp', '/dev/shm']
        results = {}
        
        for dir_path in test_dirs:
            try:
                # Check if directory exists
                dir_exists = os.path.isdir(dir_path)
                
                # Check if writable by trying to create a temporary file
                is_writable = False
                if dir_exists:
                    try:
                        test_file = os.path.join(dir_path, 'test_write.tmp')
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        is_writable = True
                    except Exception as e:
                        is_writable = False
                
                results[dir_path] = {
                    "exists": dir_exists,
                    "writable": is_writable
                }
            except Exception as e:
                results[dir_path] = {
                    "exists": "error",
                    "writable": False,
                    "error": str(e)
                }
                
        return results