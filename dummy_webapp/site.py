# site.py
# Simple Flask app that logs events to dummy_webapp/logs.txt

from flask import Flask, request, jsonify
import json, datetime, os

app = Flask(__name__)
LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs.txt')

def write_log(entry):
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")

@app.route('/')
def home():
    entry = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'event': 'page_view',
        'message': f"Page viewed {request.path}",
    }
    write_log(entry)
    return "Demo Home"

@app.route('/login', methods=['POST'])
def login():
    # Accept form or JSON
    if request.is_json:
        body = request.get_json()
        user = body.get('user')
        password = body.get('pass')
    else:
        user = request.form.get('user')
        password = request.form.get('pass')

    success = (user == 'alice' and password == 'wonderland')
    evt = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'event': 'login_attempt',
        'user': user,
        'message': 'successful_login' if success else 'failed_login'
    }
    write_log(evt)
    return jsonify({'ok': success})

@app.route('/api/data')
def api_data():
    entry = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'event': 'api_request',
        'message': f"Request to /api/data with query {dict(request.args)}"
    }
    write_log(entry)
    return jsonify({'data': 'some public data'})

# endpoint to simulate an admin-only page
@app.route('/admin')
def admin_page():
    entry = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'ip': request.remote_addr,
        'event': 'admin_access',
        'message': f"Attempt to access admin page"
    }
    write_log(entry)
    return ("Admin page (demo) - access logged", 403)

if __name__ == '__main__':
    # ensure logs directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    app.run(port=8000)
