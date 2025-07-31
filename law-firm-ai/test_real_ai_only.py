#!/usr/bin/env python3
"""
Test REAL AI generation only - no mock responses allowed
"""

import requests
import json

def test_real_ai_only():
    url = "http://localhost:8002/api/generate"  # New port
    
    data = {
        "text": "George and Chris need a Non-Disclosure Agreement (NDA) for their Lawyer AI project. George is the developer and Chris is the client. They need to protect confidential information shared during development.",
        "context": "NDA"
    }
    
    print("=" * 60)
    print("TESTING REAL AI GENERATION ONLY")
    print("=" * 60)
    print(f"Request: {data}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=data, timeout=60)  # Longer timeout for AI
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS!")
            
            stats = result['processing_stats']
            print(f"Together.ai Used: {stats.get('together_ai_used', False)}")
            print(f"Real AI Generation: {stats.get('real_ai_generation', False)}")
            print(f"AI Model: {stats.get('ai_model', 'unknown')}")
            print(f"Document Type: {stats.get('document_type', 'unknown')}")
            print(f"Processing Time: {stats.get('processing_time', 0)}s")
            print(f"Output Length: {stats.get('output_length', 0)} chars")
            
            print("\n" + "=" * 60)
            print("GENERATED DOCUMENT:")
            print("=" * 60)
            print(result['generated_doc'])
            print("=" * 60)
            
            # Check for mock patterns
            doc = result['generated_doc']
            if "Mock-Antwort" in doc:
                print("\n❌ FAILURE: Still contains mock response!")
            elif "RECHTSDOKUMENT" in doc and "Aktenzeichen:" in doc:
                print("\n❌ FAILURE: Still using old template format!")
            else:
                print("\n✅ SUCCESS: Real AI-generated document!")
                
        else:
            print("FAILED!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_real_ai_only()