from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handler(path):
    return jsonify({
        "message": "Hello from Vercel Serverless Function!",
        "path": path,
        "status": "OK"
    })

if __name__ == '__main__':
    app.run(debug=True)