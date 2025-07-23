#!/usr/bin/env python3
"""
Simple PII Remover for German Legal Documents
Focus on real-time anonymization without LLM complexity
"""

import spacy
import re
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

# Setup
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PIIEntity:
    """Simple PII entity representation"""
    type: str
    start: int
    end: int
    text: str
    confidence: float
    replacement: str

class SimplePIIRemover:
    """Simple, fast PII detection and removal for German legal documents"""
    
    def __init__(self):
        logger.info("Loading German NLP model...")
        try:
            self.nlp = spacy.load("de_core_news_lg")
            logger.info("✅ Loaded de_core_news_lg model")
        except OSError:
            try:
                self.nlp = spacy.load("de_core_news_md")
                logger.info("✅ Loaded de_core_news_md model") 
            except OSError:
                self.nlp = spacy.load("de_core_news_sm")
                logger.info("✅ Loaded de_core_news_sm model")
        
        # German PII patterns
        self.patterns = {
            'PERSON_NAME': {
                'description': 'Person Names',
                'icon': '👤'
            },
            'ORGANIZATION': {
                'description': 'Organizations',
                'icon': '🏢'
            },
            'LOCATION': {
                'description': 'Locations', 
                'icon': '📍'
            },
            'PHONE': {
                'description': 'Phone Numbers',
                'icon': '📞',
                'regex': r'\+49[\s\-]?\d{2,5}[\s\-]?\d{3,8}|\b0\d{2,5}[\s\-]?\d{3,8}\b'
            },
            'EMAIL': {
                'description': 'Email Addresses',
                'icon': '📧',
                'regex': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            },
            'IBAN': {
                'description': 'Bank Accounts (IBAN)',
                'icon': '💳',
                'regex': r'\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b'
            },
            'POSTAL_CODE': {
                'description': 'Postal Codes',
                'icon': '📮',
                'regex': r'\b\d{5}\b'
            },
            'CASE_NUMBER': {
                'description': 'Case Numbers',
                'icon': '📁',
                'regex': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\b'
            },
            'TAX_ID': {
                'description': 'Tax ID Numbers',
                'icon': '🆔',
                'regex': r'\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b'
            },
            'AMOUNT': {
                'description': 'Monetary Amounts',
                'icon': '💰',
                'regex': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:EUR|€|Euro)\b'
            }
        }
        
        # Words to skip (common German words)
        self.skip_words = {
            'der', 'die', 'das', 'und', 'ist', 'ein', 'eine', 'von', 'mit', 'auf',
            'für', 'zu', 'an', 'bei', 'nach', 'vor', 'über', 'unter', 'durch',
            'berlin', 'münchen', 'hamburg', 'köln', 'frankfurt', 'stuttgart',
            'deutschland', 'germany', 'pdf', 'document', 'text'
        }
    
    def detect_pii(self, text: str) -> List[PIIEntity]:
        """Detect PII entities in German text"""
        entities = []
        entity_counter = {}
        
        # NLP-based detection (persons, organizations, locations)
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.text.lower().strip() in self.skip_words:
                continue
                
            if len(ent.text.strip()) < 2:
                continue
            
            entity_type = None
            confidence = 0.8
            
            if ent.label_ in ['PER', 'PERSON']:
                entity_type = 'PERSON_NAME'
                confidence = 0.9
            elif ent.label_ in ['ORG']:
                entity_type = 'ORGANIZATION'
                confidence = 0.8
            elif ent.label_ in ['LOC', 'GPE']:
                # Skip common German cities
                if ent.text.lower() not in {'berlin', 'münchen', 'hamburg', 'köln'}:
                    entity_type = 'LOCATION'
                    confidence = 0.7
            
            if entity_type:
                # Generate replacement
                if entity_type not in entity_counter:
                    entity_counter[entity_type] = 0
                entity_counter[entity_type] += 1
                
                replacement = f"[{entity_type}_{entity_counter[entity_type]}]"
                
                entities.append(PIIEntity(
                    type=entity_type,
                    start=ent.start_char,
                    end=ent.end_char,
                    text=ent.text,
                    confidence=confidence,
                    replacement=replacement
                ))
        
        # Regex-based detection
        for pattern_name, pattern_info in self.patterns.items():
            if 'regex' not in pattern_info:
                continue
                
            regex = pattern_info['regex']
            for match in re.finditer(regex, text, re.IGNORECASE):
                # Generate replacement
                if pattern_name not in entity_counter:
                    entity_counter[pattern_name] = 0
                entity_counter[pattern_name] += 1
                
                replacement = f"[{pattern_name}_{entity_counter[pattern_name]}]"
                
                entities.append(PIIEntity(
                    type=pattern_name,
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    confidence=0.95,
                    replacement=replacement
                ))
        
        # Remove overlapping entities (keep longest/highest confidence)
        entities = self._remove_overlaps(entities)
        
        return entities
    
    def _remove_overlaps(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        """Remove overlapping entities, keeping the best ones"""
        if not entities:
            return entities
        
        # Sort by start position
        entities.sort(key=lambda e: e.start)
        
        non_overlapping = []
        for entity in entities:
            # Check if it overlaps with any existing entity
            overlaps = False
            for existing in non_overlapping:
                if not (entity.end <= existing.start or existing.end <= entity.start):
                    # They overlap - keep the longer one or higher confidence
                    if (entity.end - entity.start > existing.end - existing.start or 
                        entity.confidence > existing.confidence):
                        # Replace existing with current
                        non_overlapping.remove(existing)
                        non_overlapping.append(entity)
                    overlaps = True
                    break
            
            if not overlaps:
                non_overlapping.append(entity)
        
        return sorted(non_overlapping, key=lambda e: e.start)
    
    def anonymize_text(self, text: str, entities: List[PIIEntity]) -> str:
        """Replace PII entities with placeholders"""
        # Sort in reverse order to maintain indices
        entities_sorted = sorted(entities, key=lambda e: e.start, reverse=True)
        
        anonymized = text
        for entity in entities_sorted:
            anonymized = anonymized[:entity.start] + entity.replacement + anonymized[entity.end:]
        
        return anonymized

# Initialize PII remover
pii_remover = SimplePIIRemover()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "Simple PII Remover"})

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
        
        # Detect PII
        entities = pii_remover.detect_pii(text)
        
        # Anonymize text
        anonymized_text = pii_remover.anonymize_text(text, entities)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response
        entity_summary = {}
        detailed_entities = []
        
        for entity in entities:
            pattern_info = pii_remover.patterns.get(entity.type, {})
            
            # Summary by type
            if entity.type not in entity_summary:
                entity_summary[entity.type] = {
                    'count': 0,
                    'description': pattern_info.get('description', entity.type),
                    'icon': pattern_info.get('icon', '🔍')
                }
            entity_summary[entity.type]['count'] += 1
            
            # Detailed info
            detailed_entities.append({
                'type': entity.type,
                'original': entity.text,
                'replacement': entity.replacement,
                'position': f"{entity.start}-{entity.end}",
                'confidence': round(entity.confidence, 2)
            })
        
        return jsonify({
            "success": True,
            "original_text": text,
            "anonymized_text": anonymized_text,
            "processing_time": round(processing_time, 3),
            "entities_found": len(entities),
            "entity_summary": entity_summary,
            "detailed_entities": detailed_entities,
            "stats": {
                "original_length": len(text),
                "anonymized_length": len(anonymized_text),
                "reduction_ratio": round((len(text) - len(anonymized_text)) / len(text) * 100, 1) if text else 0
            }
        })
        
    except Exception as e:
        logger.error(f"PII detection error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Simple PII Remover Service")
    app.run(host='0.0.0.0', port=5002, debug=True)