#!/usr/bin/env python3
"""
Quick test to check if FastAPI server is responding
"""

import requests
import json
import time
from datetime import datetime

def test_server():
    base_url = "http://localhost:8001"
    
    print(f"Testing FastAPI server at {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("1. Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    
    # Test generate endpoint
    try:
        print("2. Testing /api/generate endpoint...")
        test_data = {
            "text": "Ich benötige eine Mahnung für eine überfällige Rechnung.",
            "context": "Erste Mahnung"
        }
        response = requests.post(f"{base_url}/api/generate", 
                               json=test_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Generated Doc Length: {len(data.get('generated_doc', ''))}")
            print(f"   Processing Time: {data.get('processing_stats', {}).get('processing_time')}s")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print()
    print("Test completed at:", datetime.now().strftime('%H:%M:%S'))

if __name__ == "__main__":
    test_server()