# web_panel_flask.py
from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

bots = {}  # hostname: {user, ip, time (str), last_seen (datetime)}
LOCK = threading.Lock()

@app.route('/')
def index():
    now = datetime.utcnow()
    with LOCK:
        for bot in bots.values():
            bot['status'] = '✅ ONLINE' if now - bot['last_seen'] < timedelta(minutes=10) else '❌ OFFLINE'
    return render_template('panel.html', bots=bots)

@app.route('/api/ping', methods=['POST'])
def ping():
    data = request.get_json()
    hostname = data.get('hostname')
    if not hostname:
        return 'Missing hostname', 400

    with LOCK:
        bots[hostname] = {
            'user': data.get('user'),
            'ip': data.get('ip'),
            'time': data.get('time'),
            'last_seen': datetime.utcnow()
        }
    return 'OK'

@app.route('/api/bots')
def get_bots():
    with LOCK:
        return jsonify(bots)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
