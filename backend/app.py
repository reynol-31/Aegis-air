# backend/app.py
from flask import Flask, jsonify, Response, send_from_directory
from flask_cors import CORS
from monitor import LogMonitor
import os, time

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__, static_folder=None)
# allow your frontend origin (adjust if needed)
CORS(app, origins=["http://127.0.0.1:5500", "http://127.0.0.1:5000"])

# Use absolute paths so there's no ambiguity about working directory
DENYLIST_FILE = os.path.join(BASE_DIR, "denylist.txt")
LOG_FILE = os.path.join(BASE_DIR, "..", "dummy_webapp", "logs.txt")
INCIDENTS_LOG = os.path.join(BASE_DIR, "incidents.log")

monitor = LogMonitor(denylist_path=DENYLIST_FILE, incidents_log_path=INCIDENTS_LOG)

@app.route("/")
def home():
    return "AegisAIR backend running. Use /dashboard, /incidents, /denylist, /logs_tail"

# Serve frontend via backend (optional)
@app.route("/dashboard")
def serve_dashboard():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/incidents")
def incidents():
    try:
        new = monitor.classify_and_respond()  # force a pass
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # Return all incidents recorded by monitor (list)
    return jsonify(monitor.incidents)

@app.route("/denylist")
def denylist():
    if not os.path.exists(DENYLIST_FILE):
        return jsonify([])
    try:
        with open(DENYLIST_FILE, "r") as f:
            ips = [line.strip() for line in f.readlines() if line.strip()]
        return jsonify(ips)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logs_tail")
def logs_tail():
    try:
        if not os.path.exists(LOG_FILE):
            return Response("No logs file found: " + LOG_FILE, status=404, mimetype="text/plain")
        # get last 200 lines
        with open(LOG_FILE, "rb") as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            blocksize = 1024
            data = b""
            while filesize > 0 and data.count(b"\n") < 200:
                readsize = blocksize if filesize - blocksize > 0 else filesize
                f.seek(filesize - readsize)
                data = f.read(readsize) + data
                filesize -= readsize
            text = data.decode(errors="replace")
            lines = text.splitlines()[-200:]
        return Response("\n".join(lines), mimetype="text/plain")
    except Exception as e:
        return Response(f"Failed to read logs: {e}", status=500, mimetype="text/plain")

if __name__ == "__main__":
    # ensure files exist
    open(DENYLIST_FILE, "a").close()
    open(INCIDENTS_LOG, "a").close()
    app.run(host="127.0.0.1", port=5000, debug=True)
