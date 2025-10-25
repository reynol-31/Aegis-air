# secbert_handler.py (demo/mock)
# Lightweight deterministic detector for demo purposes.
import re

class SecBERTHandler:
    def __init__(self):
        print("[SecBERT MOCK] Using simple keyword-based mock classifier for demo.")

    def classify(self, text):
        txt = (text or "").lower()
        # keywords to treat as malicious
        if any(k in txt for k in ["failed_login", "failed login", "failed", "admin", "sql", "or 1=1", "attack"]):
            return "malicious", 0.99
        # brute-force heuristic: many digits with 'wrong' etc
        if re.search(r"\bwrong\b|\bunauthorized\b|\bfail\b", txt):
            return "malicious", 0.9
        return "benign", 0.99
