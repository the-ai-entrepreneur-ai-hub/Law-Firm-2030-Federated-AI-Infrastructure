#!/usr/bin/env python3
"""
Test real AI document generation with Together.ai
"""

import requests
import json
import time
from datetime import datetime

def test_real_ai_generation():
    base_url = "http://localhost:8001"
    
    print("=" * 60)
    print("Testing Real AI Document Generation")
    print("=" * 60)
    print(f"Server: {base_url}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Test cases with German legal contexts
    test_cases = [
        {
            "name": "NDA (Geheimhaltungsvereinbarung)",
            "text": "George and Chris did a project on Lawyer AI. George is developer and Chris is Client. They need an NDA to protect confidential information shared during development.",
            "context": "NDA"  # This should trigger DocumentType.GEHEIMHALTUNG
        },
        {
            "name": "Mahnung (Payment Reminder)", 
            "text": "Ich benötige eine Mahnung für eine überfällige Rechnung über 2.500 EUR von einem Kunden, der seit 45 Tagen nicht gezahlt hat.",
            "context": "Mahnung, Zahlungsverzug"  # This should trigger DocumentType.MAHNUNG
        },
        {
            "name": "Legal Consultation Response",
            "text": "Ein Mandant möchte wissen, ob er einen Online-Kaufvertrag widerrufen kann, der vor 8 Tagen abgeschlossen wurde.",
            "context": "Widerrufsrecht, E-Commerce"  # This should trigger DocumentType.ALLGEMEIN
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * (len(test_case['name']) + 12))
        
        try:
            start_time = time.time()
            
            # Call the generate endpoint
            response = requests.post(f"{base_url}/api/generate", 
                                   json={
                                       "text": test_case["text"],
                                       "context": test_case["context"]
                                   }, 
                                   timeout=30)  # Longer timeout for AI generation
            
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"[SUCCESS] AI Generation completed in {request_time:.2f}s")
                
                # Show statistics
                stats = result['processing_stats']
                print(f"Document Type: {stats.get('document_type', 'unknown')}")
                print(f"AI Model: {stats.get('ai_model', 'unknown')}")
                print(f"Together.ai Used: {stats.get('together_ai_used', False)}")
                print(f"Processing Time: {stats.get('processing_time', 0)}s")
                print(f"Input Length: {stats.get('input_length', 0)} chars")
                print(f"Output Length: {stats.get('output_length', 0)} chars")
                print(f"Tokens Used: {stats.get('tokens_used', 0)}")
                
                # Show document preview
                document = result['generated_doc']
                print(f"\nDocument Preview:")
                print("-" * 40)
                # Show first 500 characters
                preview = document[:500] + "..." if len(document) > 500 else document
                print(preview)
                print("-" * 40)
                
                # Check if it's a real AI response (not mock)
                if "Mock-Antwort" in document:
                    print("[WARNING] Still using mock response - Together.ai may not be working")
                elif len(document) > 100 and "Sehr geehrte" in document:
                    print("[SUCCESS] Real AI-generated German legal document!")
                else:
                    print("[UNKNOWN] Response format unclear")
                    
            else:
                print(f"[FAILED] Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Exception: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("Real AI Integration Test Summary")
    print("=" * 60)
    print("The updated backend now uses:")
    print("- Together.ai API with Llama-3.1-70B-Instruct-Turbo")
    print("- German legal system prompts")
    print("- Context-aware document type detection")
    print("- Professional German legal language")
    print(f"\nCompleted at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    test_real_ai_generation()