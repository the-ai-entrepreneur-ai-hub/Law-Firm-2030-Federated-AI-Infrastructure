#!/usr/bin/env python3
"""
Standalone Debug Server for Law Firm AI
This runs separately from the main application to provide debugging and translation features.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import logging
from datetime import datetime
import os

# Create Flask app for debug server
debug_app = Flask(__name__)
CORS(debug_app)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock data storage (in production, this would connect to the main app's debug data)
debug_sessions = {}

# German to English legal terms mapping
LEGAL_TERMS_MAPPING = {
    "Rechtsanwalt": "Lawyer/Attorney",
    "Mandant": "Client", 
    "Kläger": "Plaintiff",
    "Beklagte": "Defendant", 
    "Amtsgericht": "Local Court",
    "Landgericht": "Regional Court",
    "Bundesgerichtshof": "Federal Court of Justice",
    "Klageerhebung": "Filing a Lawsuit",
    "Unterlassungserklärung": "Cease and Desist Declaration",
    "Schadensersatz": "Damages/Compensation",
    "Urheberrechtsverletzung": "Copyright Infringement",
    "Arbeitsrecht": "Labor Law",
    "Bürgerliches Gesetzbuch": "Civil Code",
    "Ersteinschätzung": "Initial Assessment",
    "Rechtslage": "Legal Situation",
    "Anspruchsgrundlage": "Legal Basis for Claim",
    "Erfolgsaussichten": "Chances of Success",
    "Verjährung": "Statute of Limitations",
    "Prozesskostenhilfe": "Legal Aid",
    "Verzugszinsen": "Default Interest",
    "außerordentliche Kündigung": "Extraordinary Termination",
    "Entgeltfortzahlungsanspruch": "Continued Payment Claim",
    "Verwertungsrechte": "Exploitation Rights",
    "Lizenzschaden": "License Damage",
    "entgangener Gewinn": "Lost Profit"
}

def simple_translate(german_text):
    """Simple translation using term mapping."""
    translated = german_text
    for german_term, english_term in LEGAL_TERMS_MAPPING.items():
        translated = translated.replace(german_term, f"{english_term} ({german_term})")
    return translated

@debug_app.route('/health', methods=['GET'])
def health_check():
    """Health check for debug server."""
    return jsonify({
        "service": "Law Firm AI Debug Server",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "German-to-English translation",
            "Real-time processing monitoring",
            "PII detection analysis",
            "Debug session tracking"
        ],
        "timestamp": datetime.now().isoformat()
    })

@debug_app.route('/', methods=['GET'])
def serve_monitor():
    """Serve the debug monitoring interface."""
    try:
        with open('debug_monitor.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return jsonify({"error": "Debug monitor interface not found"}), 404

@debug_app.route('/debug/sessions', methods=['GET'])
def get_debug_sessions():
    """Get all debug sessions."""
    # Create sample data to demonstrate the interface
    sample_sessions = [
        {
            "processing_id": "abc12345",
            "filename": "sample_contract.pdf",
            "start_time": datetime.now().isoformat(),
            "status": "completed",
            "steps_completed": 4,
            "pii_entities_found": 8
        },
        {
            "processing_id": "def67890",
            "filename": "legal_document.docx", 
            "start_time": datetime.now().isoformat(),
            "status": "started",
            "steps_completed": 2,
            "pii_entities_found": 3
        }
    ]
    
    return jsonify({
        "total_sessions": len(sample_sessions),
        "sessions": sample_sessions,
        "note": "This is a standalone debug server. Connect to main app for live data."
    })

@debug_app.route('/debug/session/<processing_id>', methods=['GET'])
def get_debug_session(processing_id):
    """Get detailed debug session data."""
    # Sample detailed session data
    sample_session = {
        "processing_id": processing_id,
        "filename": "sample_document.pdf",
        "start_time": datetime.now().isoformat(),
        "status": "completed",
        "steps": [
            {
                "step_name": "file_upload",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "filename": "sample_document.pdf",
                    "status": "File received and validation started",
                    "status_english": "File received and validation started"
                }
            },
            {
                "step_name": "ocr_extraction", 
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "extracted_text_preview": "An das Amtsgericht München. Sehr geehrte Damen und Herren, hiermit erheben wir Klage...",
                    "extracted_text_preview_english": "To the Local Court Munich. Dear Ladies and Gentlemen, we hereby file a lawsuit...",
                    "text_length": 1250,
                    "processing_time_seconds": 2.5,
                    "status": "OCR extraction completed",
                    "status_english": "OCR extraction completed"
                }
            }
        ],
        "pii_analysis": {
            "original_text_german": "Max Mustermann, wohnhaft in München, Musterstraße 123...",
            "original_text_english": "Max Mustermann (Person Name), residing in Munich (Location), Sample Street 123...",
            "anonymized_text_german": "[PERSON_1], wohnhaft in [LOC_1], [ADDRESS_1]...",
            "anonymized_text_english": "[PERSON_1], residing in [LOC_1], [ADDRESS_1]...",
            "entities_found": 8,
            "total_text_length": 1250,
            "pii_samples_english": {
                "PERSON": [
                    {
                        "placeholder": "[PERSON_1]",
                        "original_german": "Max Mustermann",
                        "english_translation": "Max Mustermann (Person Name)",
                        "type": "Person Name"
                    }
                ],
                "LOC": [
                    {
                        "placeholder": "[LOC_1]",
                        "original_german": "München",
                        "english_translation": "Munich (Location)",
                        "type": "Location"
                    }
                ]
            }
        },
        "llm_interaction": {
            "input_text_german": "Analysieren Sie bitte das folgende rechtliche Dokument: [PERSON_1] gegen [ORG_1]...",
            "input_text_english": "Please analyze the following legal document: [PERSON_1] versus [ORG_1]...",
            "llm_response_german": "**BETREFF:** Lohnklage gegen [ORG_1] - 3.000 EUR Gehaltszahlung...",
            "llm_response_english": "**SUBJECT:** Wage lawsuit against [ORG_1] - 3,000 EUR salary payment...",
            "input_length": 500,
            "response_length": 800,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    return jsonify({
        "debug_session": sample_session,
        "note": "This is sample data from the standalone debug server"
    })

@debug_app.route('/debug/translate', methods=['POST'])
def translate_text():
    """Translate German text to English."""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Please provide 'text' field in JSON body"}), 400
    
    german_text = data['text']
    context = data.get('context', 'legal')
    
    # Simple translation using term mapping
    english_translation = simple_translate(german_text)
    
    return jsonify({
        "original_german": german_text,
        "english_translation": english_translation,
        "context": context,
        "method": "term_mapping",
        "timestamp": datetime.now().isoformat(),
        "note": "This is a simplified translation using legal term mapping"
    })

@debug_app.route('/api/main-app-status', methods=['GET'])
def check_main_app():
    """Check if the main Law Firm AI app is running."""
    try:
        import requests
        response = requests.get('http://localhost:5001/health', timeout=5)
        if response.status_code == 200:
            return jsonify({
                "main_app_status": "running",
                "main_app_data": response.json(),
                "connection": "connected"
            })
        else:
            return jsonify({
                "main_app_status": "error",
                "connection": "failed",
                "status_code": response.status_code
            })
    except Exception as e:
        return jsonify({
            "main_app_status": "offline",
            "connection": "failed",
            "error": str(e),
            "note": "Debug server running in standalone mode"
        })

if __name__ == '__main__':
    logger.info("🔍 Starting Law Firm AI Debug Server...")
    logger.info("📊 Debug Interface: http://localhost:5002")
    logger.info("🔄 Translation API: http://localhost:5002/debug/translate")
    debug_app.run(host='0.0.0.0', port=5002, debug=True)