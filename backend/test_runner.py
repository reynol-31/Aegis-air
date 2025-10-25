# test_runner.py
# Lightweight offline runner to inspect last logs, classification, and playbook outcomes.

import os, json, sys
from monitor import LogMonitor
from response_engine import run_playbook

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "dummy_webapp", "logs.txt")

def tail_logs(n=50):
    if not os.path.exists(LOG_FILE):
        print("No logs file:", LOG_FILE); return []
    with open(LOG_FILE, "rb") as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        block = 4096
        data = b""
        while filesize > 0 and data.count(b"\n") < n:
            readsize = min(block, filesize)
            f.seek(filesize - readsize)
            data = f.read(readsize) + data
            filesize -= readsize
        text = data.decode(errors="replace")
        lines = [l for l in text.splitlines() if l.strip()]
    return [json.loads(l) for l in lines[-n:]]

def main():
    print("Loading monitor & classifier...")
    m = LogMonitor()
    logs = tail_logs(100)
    if not logs:
        print("No logs to process.")
        return
    print(f"Processing {len(logs)} logs (most recent last):\n")
    any_mal = False
    for i, evt in enumerate(logs, 1):
        text = evt.get("message") or evt.get("event") or json.dumps(evt)
        label, prob = m.secbert.classify(text)
        print(f"[{i}] IP={evt.get('ip')} event={evt.get('event')} message={text}")
        print(f"     -> classification: {label} (conf={prob:.3f})")
        if label == "malicious":
            any_mal = True
            # show playbook actions (simulate)
            acts = run_playbook(evt)
            print("     -> playbook actions:", acts)
        else:
            print("     -> no playbook action (benign)")
        print("-" * 60)
    if not any_mal:
        print("\nNo logs classified as malicious. Suggestions below.")
    else:
        print("\nSome logs were classified malicious and playbook actions were printed above.")

if __name__ == "__main__":
    main()
