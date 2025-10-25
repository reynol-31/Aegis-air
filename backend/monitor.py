# monitor.py
import os
import time
import json
from secbert_handler import SecBERTHandler
from response_engine import run_playbook

class LogMonitor:
    def __init__(self, log_path=None, denylist_path=None, incidents_log_path=None):
        # paths may be passed from app; otherwise default relative path
        base = os.path.dirname(__file__)
        self.log_path = log_path or os.path.join(base, "..", "dummy_webapp", "logs.txt")
        self.denylist_path = denylist_path or os.path.join(base, "denylist.txt")
        self.incidents_log_path = incidents_log_path or os.path.join(base, "incidents.log")

        print(f"[Monitor] LOG_FILE = {self.log_path}")
        print(f"[Monitor] DENYLIST = {self.denylist_path}")
        print(f"[Monitor] INCIDENTS_LOG = {self.incidents_log_path}")

        self.secbert = SecBERTHandler()
        self.last_pos = 0
        self.incidents = []  # in-memory list of incident strings

    def tail_logs(self):
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(self.last_pos)
            lines = f.readlines()
            self.last_pos = f.tell()
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                result.append(json.loads(line))
            except Exception:
                result.append({"ip":"unknown", "message": line})
        return result

    def classify_and_respond(self):
        """
        Tail logs, classify lines, run playbook for malicious ones.
        Returns list of new incident strings created during this pass.
        """
        logs = self.tail_logs()
        new_incidents = []
        for evt in logs:
            text = evt.get("message") or evt.get("event") or json.dumps(evt)
            label, prob = self.secbert.classify(text)
            print(f"[Monitor] {evt.get('ip')} -> {label} (conf={prob:.2f}) text='{text}'")
            if label == "malicious":
                # run playbook; run_playbook returns list of incident strings it created
                created = run_playbook(evt, denylist_path=self.denylist_path, incidents_log_path=self.incidents_log_path)
                if created:
                    new_incidents.extend(created)
                    # also append to in-memory incidents
                    self.incidents.extend(created)
        return new_incidents
