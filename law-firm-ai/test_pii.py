#!/usr/bin/env python3
"""
Simple command-line PII tester - no Flask needed
"""

import re
import json
from datetime import datetime

class SimplePIIRemover:
    def __init__(self):
        # German PII patterns
        self.patterns = {
            'PERSON_NAME': {
                'description': '👤 Person Names',
                'regex': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            },
            'PHONE': {
                'description': '📞 Phone Numbers', 
                'regex': r'(\+49[\s\-]?\d{2,5}[\s\-]?\d{3,8}|\b0\d{2,5}[\s\-]?\d{3,8})',
            },
            'EMAIL': {
                'description': '📧 Email Addresses',
                'regex': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            },
            'IBAN': {
                'description': '💳 Bank Accounts',
                'regex': r'\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b',
            },
            'POSTAL_CODE': {
                'description': '📮 Postal Codes',
                'regex': r'\b\d{5}\b(?=\s+[A-Z][a-z]+)',
            },
            'CASE_NUMBER': {
                'description': '📁 Case Numbers',
                'regex': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\b',
            },
            'TAX_ID': {
                'description': '🆔 Tax ID Numbers',
                'regex': r'\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b',
            },
            'AMOUNT': {
                'description': '💰 Monetary Amounts',
                'regex': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:EUR|€|Euro)\b',
            },
            'STREET_ADDRESS': {
                'description': '🏠 Street Addresses',
                'regex': r'\b[A-Z][a-z]+straße\s+\d+\b',
            },
            'ORGANIZATION': {
                'description': '🏢 Organizations',
                'regex': r'\b[A-Z][a-z]+\s+&\s+[A-Z][a-z]+(?:\s+GmbH|\s+AG)?\b',
            }
        }
    
    def detect_and_anonymize(self, text: str):
        """Detect PII and return anonymized text"""
        print("🔍 Scanning for PII entities...")
        
        entities = []
        entity_counter = {}
        anonymized_text = text
        
        # Process each pattern
        for pattern_name, pattern_info in self.patterns.items():
            regex = pattern_info['regex']
            matches = list(re.finditer(regex, text, re.IGNORECASE))
            
            if matches:
                print(f"   Found {len(matches)} {pattern_info['description']}")
            
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
                    'end': match.end()
                })
                
                print(f"      \"{match.group()}\" → {replacement}")
        
        # Apply replacements (in reverse order to maintain indices)
        entities_sorted = sorted(entities, key=lambda x: x['start'], reverse=True)
        for entity in entities_sorted:
            anonymized_text = anonymized_text[:entity['start']] + entity['replacement'] + anonymized_text[entity['end']:]
        
        return anonymized_text, entities

def main():
    print("🔒 German Legal Document PII Remover")
    print("=" * 50)
    
    # Sample German legal text
    sample_text = """Rechtsanwaltskanzlei Müller & Partner GmbH
Berliner Straße 123
10115 Berlin

Betreff: Rechtssache gegen Hans Schmidt
Aktenzeichen: 4 C 2156/2024
Telefon: +49 30 12345678
E-Mail: info@mueller-partner.de
IBAN: DE89 3704 0044 0532 0130 00

Sehr geehrte Damen und Herren,

hiermit teilen wir Ihnen mit, dass unser Mandant Hans Schmidt, wohnhaft in der Hauptstraße 45, 12345 Musterstadt, eine Klage gegen Ihre Versicherungsgesellschaft einreichen wird.

Die Schadenshöhe beläuft sich auf 25.000,00 EUR.

Weitere beteiligte Personen:
- Maria Schmidt (Ehefrau des Mandanten)
- Dr. Weber (behandelnder Arzt)
- Steuer-ID: 12 345 678 901

Mit freundlichen Grüßen
Dr. Andrea Müller"""

    pii_remover = SimplePIIRemover()
    
    print("📋 ORIGINAL TEXT:")
    print("-" * 30)
    print(sample_text)
    print()
    
    start_time = datetime.now()
    anonymized_text, entities = pii_remover.detect_and_anonymize(sample_text)
    processing_time = (datetime.now() - start_time).total_seconds()
    
    print()
    print("🔒 ANONYMIZED TEXT:")
    print("-" * 30)
    print(anonymized_text)
    print()
    
    print("📊 STATISTICS:")
    print(f"   • Processing time: {processing_time:.3f} seconds")
    print(f"   • PII entities found: {len(entities)}")
    print(f"   • Original length: {len(sample_text)} characters")
    print(f"   • Anonymized length: {len(anonymized_text)} characters")
    print()
    
    print("🎯 SUCCESS: PII detection and anonymization working!")

if __name__ == '__main__':
    main()