from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/data')
def data():
    return jsonify({"internal": "This came from backend:5555"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
