#!/usr/bin/env python3
"""
Simple PII test without Docker - using basic regex patterns only
"""

import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

class RegexPIIRemover:
    """Simple regex-based PII remover for quick testing"""
    
    def __init__(self):
        # German PII patterns
        self.patterns = {
            'PERSON_NAME': {
                'description': 'Person Names',
                'icon': '👤',
                'regex': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Simple name pattern
                'examples': ['Hans Schmidt', 'Maria Müller']
            },
            'PHONE': {
                'description': 'Phone Numbers', 
                'icon': '📞',
                'regex': r'(\+49[\s\-]?\d{2,5}[\s\-]?\d{3,8}|\b0\d{2,5}[\s\-]?\d{3,8})',
                'examples': ['+49 30 12345678', '0171 9876543']
            },
            'EMAIL': {
                'description': 'Email Addresses',
                'icon': '📧', 
                'regex': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'examples': ['info@example.de']
            },
            'IBAN': {
                'description': 'Bank Accounts',
                'icon': '💳',
                'regex': r'\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b',
                'examples': ['DE89 3704 0044 0532 0130 00']
            },
            'POSTAL_CODE': {
                'description': 'Postal Codes',
                'icon': '📮',
                'regex': r'\b\d{5}\b(?=\s+[A-Z][a-z]+)',  # 5 digits followed by city
                'examples': ['10115', '12345']
            },
            'CASE_NUMBER': {
                'description': 'Case Numbers',
                'icon': '📁',
                'regex': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\b',
                'examples': ['4 C 2156/2024']
            },
            'TAX_ID': {
                'description': 'Tax ID Numbers',
                'icon': '🆔',
                'regex': r'\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b',
                'examples': ['12 345 678 901']
            },
            'AMOUNT': {
                'description': 'Monetary Amounts',
                'icon': '💰',
                'regex': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:EUR|€|Euro)\b',
                'examples': ['25.000,00 EUR']
            },
            'STREET_ADDRESS': {
                'description': 'Street Addresses',
                'icon': '🏠',
                'regex': r'\b[A-Z][a-z]+straße\s+\d+\b',
                'examples': ['Berliner Straße 123']
            },
            'ORGANIZATION': {
                'description': 'Organizations',
                'icon': '🏢',
                'regex': r'\b[A-Z][a-z]+\s+&\s+[A-Z][a-z]+(?:\s+GmbH|\s+AG)?\b',
                'examples': ['Müller & Partner GmbH']
            }
        }
    
    def detect_and_anonymize(self, text: str):
        """Detect PII and return anonymized text"""
        entities = []
        entity_counter = {}
        anonymized_text = text
        
        # Process each pattern
        for pattern_name, pattern_info in self.patterns.items():
            regex = pattern_info['regex']
            matches = list(re.finditer(regex, text, re.IGNORECASE))
            
            for match in matches:
                # Generate replacement
                if pattern_name not in entity_counter:
                    entity_counter[pattern_name] = 0
                entity_counter[pattern_name] += 1
                
                replacement = f"[{pattern_name}_{entity_counter[pattern_name]}]"
                
                entities.append({
                    'type': pattern_name,
                    'original': match.group(),
                    'replacement': replacement,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.9
                })
        
        # Remove overlapping entities
        entities = self._remove_overlaps(entities)
        
        # Apply replacements (in reverse order to maintain indices)
        entities_sorted = sorted(entities, key=lambda x: x['start'], reverse=True)
        for entity in entities_sorted:
            anonymized_text = anonymized_text[:entity['start']] + entity['replacement'] + anonymized_text[entity['end']:]
        
        return anonymized_text, entities
    
    def _remove_overlaps(self, entities):
        """Remove overlapping entities"""
        if not entities:
            return entities
        
        # Sort by start position
        entities.sort(key=lambda x: x['start'])
        
        non_overlapping = []
        for entity in entities:
            # Check if it overlaps with existing entities
            overlaps = False
            for existing in non_overlapping:
                if not (entity['end'] <= existing['start'] or existing['end'] <= entity['start']):
                    # They overlap - keep the longer one
                    if entity['end'] - entity['start'] > existing['end'] - existing['start']:
                        non_overlapping.remove(existing)
                        non_overlapping.append(entity)
                    overlaps = True
                    break
            
            if not overlaps:
                non_overlapping.append(entity)
        
        return non_overlapping

# Initialize PII remover
pii_remover = RegexPIIRemover()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Regex PII Remover"})

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
        anonymized_text, entities = pii_remover.detect_and_anonymize(text)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response
        entity_summary = {}
        
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in entity_summary:
                pattern_info = pii_remover.patterns[entity_type]
                entity_summary[entity_type] = {
                    'count': 0,
                    'description': pattern_info['description'],
                    'icon': pattern_info['icon']
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

if __name__ == '__main__':
    print("🚀 Starting Simple PII Remover Service on http://localhost:5002")
    print("📝 Open pii_test.html in your browser to test")
    app.run(host='0.0.0.0', port=5002, debug=True)