@echo off
echo Starting PDF PII Anonymizer Server...
cd "C:\Users\Administrator\serveless-apps\Law Firm Vision 2030\law-firm-ai"
call pii_env\Scripts\activate.bat
python pdf_pii_web_app.py
pause