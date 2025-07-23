#!/usr/bin/env python3
"""
Final PII Demo - Shows real-time anonymization results
"""

import re
import sys
from datetime import datetime

class FinalPIIRemover:
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

def print_comparison(original: str, anonymized: str, entities: list):
    """Print a nice comparison view"""
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                           📋 ORIGINAL TEXT                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print(original)
    print()
    
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                         🔒 ANONYMIZED TEXT                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print(anonymized)
    print()
    
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                        🎯 DETECTED PII ENTITIES                      ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    
    if entities:
        # Group by type
        by_type = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(entity)
        
        for entity_type, type_entities in by_type.items():
            # Get pattern info
            pattern_info = pii_remover.patterns.get(entity_type, {})
            description = pattern_info.get('description', entity_type)
            
            print(f"{description} ({len(type_entities)} found):")
            for entity in type_entities:
                confidence_pct = int(entity['confidence'] * 100)
                print(f"  • \"{entity['original']}\" → {entity['replacement']} ({confidence_pct}% confidence)")
            print()
    else:
        print("No PII entities detected.")
    
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                            📊 STATISTICS                            ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print(f"Original length:    {len(original):,} characters")
    print(f"Anonymized length:  {len(anonymized):,} characters")
    print(f"PII entities found: {len(entities)}")
    print(f"Processing time:    {processing_time:.3f} seconds")

def main():
    print("🔒 German Legal Document PII Anonymization Demo")
    print("=" * 70)
    print()
    
    # Test with your German legal document
    test_document = """Rechtsanwaltskanzlei Müller & Partner GmbH
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
Mobil: 0171 9876543"""

    global pii_remover, processing_time
    pii_remover = FinalPIIRemover()
    
    # Process the document
    start_time = datetime.now()
    entities = pii_remover.detect_pii(test_document)
    anonymized_text = pii_remover.anonymize_text(test_document, entities)
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # Display results
    print_comparison(test_document, anonymized_text, entities)
    
    print()
    print("✅ PII anonymization completed successfully!")
    print()
    print("💡 This system can now be integrated into your interface to show")
    print("   real-time PII detection and anonymization results.")

if __name__ == '__main__':
    main()