# AegisAIR — SecBERT MVP

## Overview
AegisAIR is a hackathon-ready demo: SecBERT classifies dummy webapp logs and a playbook simulates automatic responses (block IP, alert).

## Setup
1. Create & activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv/bin/activate
pip install -r requirements.txt

python dummy_webapp/site.py

cd backend
python app.py

http://127.0.0.1:5000

