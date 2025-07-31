#!/usr/bin/env python3
"""
Test single AI document generation
"""

import requests
import json

def test_single_generation():
    url = "http://localhost:8001/api/generate"
    
    data = {
        "text": "George and Chris need a Non-Disclosure Agreement (NDA) for their Lawyer AI project. George is the developer and Chris is the client. They need to protect confidential information shared during development.",
        "context": "NDA"
    }
    
    print("Testing single AI document generation...")
    print(f"Request: {data}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS!")
            print(f"Together.ai Used: {result['processing_stats'].get('together_ai_used', False)}")
            print(f"AI Model: {result['processing_stats'].get('ai_model', 'unknown')}")
            print(f"Document Type: {result['processing_stats'].get('document_type', 'unknown')}")
            print(f"Processing Time: {result['processing_stats'].get('processing_time', 0)}s")
            print("\nGenerated Document:")
            print("=" * 50)
            print(result['generated_doc'])
            print("=" * 50)
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_single_generation()