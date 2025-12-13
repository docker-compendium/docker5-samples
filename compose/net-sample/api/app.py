from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    # Internal communication with backend on port 5555
    backend_response = requests.get('http://backend:5555/data').json()
    return jsonify({
        "message": "Hello World",
        "backend_data": backend_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088)
