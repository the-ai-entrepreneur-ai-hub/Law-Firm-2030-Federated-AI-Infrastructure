#!/usr/bin/env python3
"""
Test script to verify translation functionality works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from googletrans import Translator
    
    # Test translation
    translator = Translator()
    
    # Test German to English translation
    german_text = "Dies ist ein deutscher Rechtstext mit personenbezogenen Daten."
    print(f"Original German text: {german_text}")
    
    translated = translator.translate(german_text, src='de', dest='en')
    print(f"Translated to English: {translated.text}")
    
    # Test PII anonymization example
    anonymized_german = "Dies ist ein Text mit [PER_1] und [IBAN_1] sowie [TELEFON_1]."
    print(f"\nAnonymized German text: {anonymized_german}")
    
    translated_anon = translator.translate(anonymized_german, src='de', dest='en')
    print(f"Translated anonymized text: {translated_anon.text}")
    
    print("\n✅ Translation functionality is working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install googletrans: pip install googletrans==4.0.0rc1")
except Exception as e:
    print(f"❌ Translation error: {e}")