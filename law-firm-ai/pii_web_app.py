#!/usr/bin/env python3
"""
PII Web Application - Simple Flask server for real-time PII anonymization
"""

import re
import json
from datetime import datetime

try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
    flask_available = True
except ImportError:
    flask_available = False

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔒 PII Anonymizer - Law Firm Vision 2030</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 30px;
        }
        .input-section, .output-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e9ecef;
        }
        .section-title {
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        textarea {
            width: 100%;
            height: 300px;
            padding: 15px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        .btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin: 10px 0;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { font-size: 0.9em; color: #7f8c8d; margin-top: 5px; }
        .entities-list {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            max-height: 200px;
            overflow-y: auto;
        }
        .entity-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin: 5px 0;
            background: #f1f3f4;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
        }
        .loading::after {
            content: "...";
            animation: dots 1.5s infinite;
        }
        @keyframes dots {
            0%, 20% { content: "."; }
            40% { content: ".."; }
            60%, 100% { content: "..."; }
        }
        .example-btn {
            background: #95a5a6;
            margin: 5px;
            padding: 10px 15px;
            font-size: 14px;
            width: auto;
        }
        .examples {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }
        @media (max-width: 768px) {
            .main-content { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 PII Anonymizer</h1>
            <p>Real-time German Legal Document Processing</p>
        </div>
        
        <div class="main-content">
            <div class="input-section">
                <div class="section-title">
                    📝 Input Text
                </div>
                <textarea id="inputText" placeholder="Paste your German legal document here..."></textarea>
                
                <div class="examples">
                    <button class="btn example-btn" onclick="loadExample()">📄 Load Example</button>
                    <button class="btn example-btn" onclick="clearText()">🗑️ Clear</button>
                </div>
                
                <button class="btn" onclick="processText()">🔍 Detect & Anonymize PII</button>
            </div>
            
            <div class="output-section">
                <div class="section-title">
                    🔒 Anonymized Result
                </div>
                <textarea id="outputText" readonly placeholder="Anonymized text will appear here..."></textarea>
                
                <div class="stats" id="stats" style="display: none;">
                    <div class="stat-box">
                        <div class="stat-number" id="entitiesCount">0</div>
                        <div class="stat-label">PII Entities</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="processingTime">0</div>
                        <div class="stat-label">Processing (ms)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="originalLength">0</div>
                        <div class="stat-label">Original Chars</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="anonymizedLength">0</div>
                        <div class="stat-label">Anonymized Chars</div>
                    </div>
                </div>
                
                <div class="entities-list" id="entitiesList" style="display: none;"></div>
            </div>
        </div>
    </div>

    <script>
        function loadExample() {
            const example = `Rechtsanwaltskanzlei Müller & Partner GmbH
Berliner Straße 123
10115 Berlin

Betreff: Rechtssache gegen Hans Schmidt
Aktenzeichen: 4 C 2156/2024
Telefon: +49 30 12345678
E-Mail: info@mueller-partner.de
IBAN: DE89 3704 0044 0532 0130 00

Sehr geehrte Damen und Herren,

hiermit teilen wir Ihnen mit, dass unser Mandant Hans Schmidt, 
wohnhaft in der Hauptstraße 45, 12345 Musterstadt, eine Klage 
gegen Ihre Versicherungsgesellschaft einreichen wird.

Die Schadenshöhe beläuft sich auf 25.000,00 EUR.

Weitere beteiligte Personen:
- Maria Schmidt (Ehefrau des Mandanten)
- Dr. Weber (behandelnder Arzt)  
- Klaus Mustermann (Zeuge)
- Steuer-ID: 12 345 678 901

Mit freundlichen Grüßen
Dr. Andrea Müller
Rechtsanwältin

Kontakt: a.mueller@firma.de
Mobil: 0171 9876543`;
            document.getElementById('inputText').value = example;
        }
        
        function clearText() {
            document.getElementById('inputText').value = '';
            document.getElementById('outputText').value = '';
            document.getElementById('stats').style.display = 'none';
            document.getElementById('entitiesList').style.display = 'none';
        }
        
        async function processText() {
            const inputText = document.getElementById('inputText').value.trim();
            if (!inputText) {
                alert('Please enter some text to process');
                return;
            }
            
            // Show loading state
            document.getElementById('outputText').value = '🔍 Processing...';
            document.getElementById('stats').style.display = 'none';
            document.getElementById('entitiesList').style.display = 'none';
            
            try {
                const response = await fetch('/detect-pii', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: inputText })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Update output
                document.getElementById('outputText').value = data.anonymized_text;
                
                // Update stats
                document.getElementById('entitiesCount').textContent = data.entities_found;
                document.getElementById('processingTime').textContent = Math.round(data.processing_time * 1000);
                document.getElementById('originalLength').textContent = data.stats.original_length.toLocaleString();
                document.getElementById('anonymizedLength').textContent = data.stats.anonymized_length.toLocaleString();
                document.getElementById('stats').style.display = 'grid';
                
                // Update entities list
                const entitiesList = document.getElementById('entitiesList');
                if (data.entity_summary && Object.keys(data.entity_summary).length > 0) {
                    let html = '<h4>🎯 Detected PII Types:</h4>';
                    for (const [type, info] of Object.entries(data.entity_summary)) {
                        html += `
                            <div class="entity-item">
                                <span>${info.icon} ${info.description}</span>
                                <span><strong>${info.count}</strong> found</span>
                            </div>
                        `;
                    }
                    entitiesList.innerHTML = html;
                    entitiesList.style.display = 'block';
                } else {
                    entitiesList.style.display = 'none';
                }
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('outputText').value = '❌ Error processing text: ' + error.message;
            }
        }
        
        // Auto-process on Enter (Ctrl+Enter)
        document.getElementById('inputText').addEventListener('keydown', function(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                processText();
            }
        });
    </script>
</body>
</html>
"""

class WebPIIRemover:
    def __init__(self):
        # Refined patterns focused on actual PII
        self.patterns = {
            'PERSON_NAME': {
                'description': '👤 Person Names',
                'regex': r'\b(?:Dr\.?\s+|Prof\.?\s+)?[A-ZÄÖÜ][a-zäöüß]{2,}\s+[A-ZÄÖÜ][a-zäöüß]{2,}\b',
                'confidence': 0.9
            },
            'PHONE': {
                'description': '📞 Phone Numbers', 
                'regex': r'(?:\+49[\s\-/]?\d{2,5}[\s\-/]?\d{6,8}|\b0\d{3,5}[\s\-/]?\d{6,8})\b',
                'confidence': 0.95
            },
            'EMAIL': {
                'description': '📧 Email Addresses',
                'regex': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
                'confidence': 0.98
            },
            'IBAN': {
                'description': '💳 Bank Accounts (IBAN)',
                'regex': r'\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b',
                'confidence': 0.99
            },
            'POSTAL_CODE': {
                'description': '📮 Postal Codes',
                'regex': r'\b\d{5}\b(?=\s+[A-ZÄÖÜ][a-zäöüß]{3,})',
                'confidence': 0.8
            },
            'CASE_NUMBER': {
                'description': '📁 Legal Case Numbers',
                'regex': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\b',
                'confidence': 0.95
            },
            'TAX_ID': {
                'description': '🆔 Tax ID Numbers',
                'regex': r'\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b',
                'confidence': 0.95
            },
            'AMOUNT': {
                'description': '💰 Monetary Amounts',
                'regex': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:EUR|€|Euro)\b',
                'confidence': 0.9
            },
            'STREET_ADDRESS': {
                'description': '🏠 Street Addresses',
                'regex': r'\b[A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.)\s+\d+[a-z]?\b',
                'confidence': 0.85
            }
        }
        
        # Words that should never be considered person names
        self.false_positive_names = {
            'berliner straße', 'hauptstraße', 'betreff rechtssache', 'sehr geehrte',
            'damen und', 'mit freundlichen', 'versicherungsgesellschaft einreichen',
            'die schadenshöhe', 'beläuft sich', 'weitere beteiligte', 'grüßen dr'
        }
    
    def is_valid_person_name(self, name: str) -> bool:
        """Check if a detected name is actually a person name"""
        name_lower = name.lower().strip()
        
        # Skip obvious false positives
        if name_lower in self.false_positive_names:
            return False
            
        # Skip if it contains common German words that aren't names
        if any(word in name_lower for word in ['straße', 'betreff', 'sehr', 'mit', 'der', 'die', 'das']):
            return False
            
        # Skip if it ends with newlines or contains formatting
        if '\n' in name or len(name.strip()) < 6:
            return False
            
        return True
    
    def detect_pii(self, text: str):
        """Detect PII entities in text"""
        entities = []
        entity_counter = {}
        
        for pattern_name, pattern_info in self.patterns.items():
            regex = pattern_info['regex']
            matches = list(re.finditer(regex, text, re.IGNORECASE))
            
            for match in matches:
                matched_text = match.group().strip()
                
                # Special validation for person names
                if pattern_name == 'PERSON_NAME' and not self.is_valid_person_name(matched_text):
                    continue
                
                # Generate unique replacement
                if pattern_name not in entity_counter:
                    entity_counter[pattern_name] = 0
                entity_counter[pattern_name] += 1
                
                replacement = f"[{pattern_name}_{entity_counter[pattern_name]}]"
                
                entities.append({
                    'type': pattern_name,
                    'original': matched_text,
                    'replacement': replacement,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': pattern_info['confidence']
                })
        
        # Remove overlapping entities
        entities = self._remove_overlaps(entities)
        return entities
    
    def _remove_overlaps(self, entities):
        """Remove overlapping entities, keeping the best ones"""
        if not entities:
            return entities
        
        entities.sort(key=lambda x: x['start'])
        non_overlapping = []
        
        for entity in entities:
            overlaps = False
            for i, existing in enumerate(non_overlapping):
                if not (entity['end'] <= existing['start'] or existing['end'] <= entity['start']):
                    # Overlap detected - keep the one with higher confidence or more specific type
                    priority_types = ['EMAIL', 'IBAN', 'TAX_ID', 'CASE_NUMBER', 'PHONE']
                    
                    if (entity['confidence'] > existing['confidence'] or
                        entity['type'] in priority_types and existing['type'] not in priority_types):
                        non_overlapping[i] = entity
                    overlaps = True
                    break
            
            if not overlaps:
                non_overlapping.append(entity)
        
        return non_overlapping
    
    def anonymize_text(self, text: str, entities: list):
        """Apply anonymization to text"""
        # Sort in reverse order to maintain character indices
        entities_sorted = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        anonymized_text = text
        for entity in entities_sorted:
            anonymized_text = (anonymized_text[:entity['start']] + 
                             entity['replacement'] + 
                             anonymized_text[entity['end']:])
        
        return anonymized_text

def create_flask_app():
    """Create Flask app if Flask is available"""
    if not flask_available:
        print("❌ Flask not available. Installing...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors'])
            print("✅ Flask installed successfully!")
            # Re-import after installation
            global Flask, request, jsonify, render_template_string, CORS
            from flask import Flask, request, jsonify, render_template_string
            from flask_cors import CORS
        except subprocess.CalledProcessError:
            print("❌ Failed to install Flask. Please install manually: pip install flask flask-cors")
            return None
    
    app = Flask(__name__)
    CORS(app)
    pii_remover = WebPIIRemover()
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "service": "PII Anonymizer"})
    
    @app.route('/detect-pii', methods=['POST'])
    def detect_pii():
        """Detect and anonymize PII in text"""
        try:
            # Get text input
            if request.is_json:
                data = request.get_json()
                text = data.get('text', '')
            elif 'file' in request.files:
                file = request.files['file']
                text = file.read().decode('utf-8', errors='ignore')
            else:
                text = request.form.get('text', '')
            
            if not text or len(text.strip()) < 5:
                return jsonify({"error": "No text provided or text too short"}), 400
            
            start_time = datetime.now()
            
            # Detect and anonymize PII
            entities = pii_remover.detect_pii(text)
            anonymized_text = pii_remover.anonymize_text(text, entities)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare response
            entity_summary = {}
            
            for entity in entities:
                entity_type = entity['type']
                if entity_type not in entity_summary:
                    pattern_info = pii_remover.patterns[entity_type]
                    # Extract icon from description
                    desc_parts = pattern_info['description'].split(' ', 1)
                    icon = desc_parts[0] if desc_parts[0] in '👤📞📧💳📮📁🆔💰🏠' else '🔍'
                    description = desc_parts[1] if len(desc_parts) > 1 else pattern_info['description']
                    
                    entity_summary[entity_type] = {
                        'count': 0,
                        'description': description,
                        'icon': icon
                    }
                entity_summary[entity_type]['count'] += 1
            
            return jsonify({
                "success": True,
                "original_text": text,
                "anonymized_text": anonymized_text,
                "processing_time": round(processing_time, 3),
                "entities_found": len(entities),
                "entity_summary": entity_summary,
                "detailed_entities": entities,
                "stats": {
                    "original_length": len(text),
                    "anonymized_length": len(anonymized_text),
                    "reduction_ratio": round((len(text) - len(anonymized_text)) / len(text) * 100, 1) if text else 0
                }
            })
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    
    return app

def main():
    """Main function to run the PII web app"""
    print("🔒 German Legal Document PII Anonymizer")
    print("=" * 50)
    
    # Try to create Flask app
    app = create_flask_app()
    if app is None:
        print("❌ Cannot create web app - Flask not available")
        return
    
    print("🚀 Starting PII Anonymizer Web Service")
    print("📍 URL: http://localhost:5003")
    print("💡 Open the URL in your browser to use the interface")
    print("✨ Features:")
    print("   • Real-time PII detection and anonymization")
    print("   • German legal document processing")
    print("   • Visual statistics and entity breakdown")
    print("   • Example document loading")
    print("")
    
    try:
        app.run(host='0.0.0.0', port=5003, debug=False)
    except KeyboardInterrupt:
        print("\n👋 PII Anonymizer stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main()