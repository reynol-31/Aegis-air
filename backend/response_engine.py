# response_engine.py
import os
import datetime
import yaml

# simple playbook in code (you can keep YAML if preferred)
PLAYBOOK = {
    "rules": [
        {
            "condition": "event == 'login_attempt' and message == 'failed_login'",
            "actions": ["count_failed_login"]
        },
        {
            "condition": "event == 'admin_access'",
            "actions": ["block_ip", "alert_admin"]
        }
    ]
}

def _write_incident(incidents_log_path, entry):
    with open(incidents_log_path, "a", encoding="utf-8") as f:
        f.write(str(entry) + "\n")

def run_playbook(event, denylist_path="denylist.txt", incidents_log_path="incidents.log"):
    """
    Minimal evaluator: checks event dict and performs actions.
    Returns list of incident strings created.
    """
    incidents = []
    ip = event.get("ip", "unknown")
    evt = event.get("event", "")
    message = event.get("message", "")

    # Rule: failed login -> increment count and block if >= 5
    if evt == "login_attempt" and message == "failed_login":
        count_file = os.path.join(os.path.dirname(denylist_path), f"{ip}_count.txt")
        try:
            count = 1
            if os.path.exists(count_file):
                with open(count_file, "r") as f:
                    count = int(f.read().strip() or "0") + 1
            with open(count_file, "w") as f:
                f.write(str(count))
        except Exception as e:
            print("[Playbook] count file error:", e)
            count = 1
        if count >= 5:
            # block ip
            if not os.path.exists(denylist_path):
                open(denylist_path, "a").close()
            with open(denylist_path, "r", encoding="utf-8") as f:
                denylist = [l.strip() for l in f.readlines() if l.strip()]
            if ip not in denylist:
                with open(denylist_path, "a", encoding="utf-8") as f:
                    f.write(ip + "\n")
                # Use an explicit UTC ISO8601 timestamp with 'Z' suffix (UTC) for clarity
                entry = f"{datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')} - IP {ip} blocked due to multiple failed logins"
                _write_incident(incidents_log_path, entry)
                incidents.append(entry)

    # Rule: admin access -> block immediately
    if evt == "admin_access":
        if not os.path.exists(denylist_path):
            open(denylist_path, "a").close()
        with open(denylist_path, "r", encoding="utf-8") as f:
            denylist = [l.strip() for l in f.readlines() if l.strip()]
        if ip not in denylist:
            with open(denylist_path, "a", encoding="utf-8") as f:
                f.write(ip + "\n")
            entry = f"{datetime.datetime.utcnow().isoformat()} - IP {ip} blocked for admin access attempt"
            _write_incident(incidents_log_path, entry)
            incidents.append(entry)

    # alert_admin action is simulated by adding an incident string
    # (You can expand actions as needed)

    return incidents
