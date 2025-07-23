#!/bin/bash
echo "Starting PDF PII Anonymizer Server..."
cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai"
source pii_env/bin/activate
python3 pdf_pii_web_app.py