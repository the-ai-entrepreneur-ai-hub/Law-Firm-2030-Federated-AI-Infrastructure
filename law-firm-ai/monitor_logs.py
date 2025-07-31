#!/usr/bin/env python3
"""
Real-time log monitoring for AnwaltsAI FastAPI Backend
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def monitor_api():
    """Monitor API with real-time logging"""
    print("AnwaltsAI FastAPI Backend - Real-time Monitor")
    print("=" * 50)
    print(f"Monitoring: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test different endpoints periodically
    test_cases = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{BASE_URL}/health",
            "interval": 30  # every 30 seconds
        },
        {
            "name": "PII Sanitization Test",
            "method": "POST", 
            "url": f"{BASE_URL}/api/sanitize",
            "data": {"text": "Test email: test@example.com and phone +49 30 12345678"},
            "interval": 60  # every 60 seconds
        }
    ]
    
    last_run = {}
    
    while True:
        try:
            current_time = time.time()
            
            for test in test_cases:
                test_name = test["name"]
                
                # Check if it's time to run this test
                if test_name not in last_run or (current_time - last_run[test_name]) >= test["interval"]:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running: {test_name}")
                    
                    try:
                        if test["method"] == "GET":
                            response = requests.get(test["url"], timeout=5)
                        else:
                            response = requests.post(test["url"], json=test["data"], timeout=10)
                        
                        if response.status_code == 200:
                            print(f"  SUCCESS - Status: {response.status_code}")
                            if test_name == "Health Check":
                                data = response.json()
                                print(f"  Service: {data.get('service', 'Unknown')}")
                                print(f"  Status: {data.get('status', 'Unknown')}")
                            elif "Sanitization" in test_name:
                                data = response.json()
                                print(f"  Entities removed: {len(data.get('entities_removed', []))}")
                                print(f"  Processing time: {data.get('processing_time', 0)}s")
                        else:
                            print(f"  FAILED - Status: {response.status_code}")
                            print(f"  Response: {response.text[:100]}...")
                            
                    except Exception as e:
                        print(f"  ERROR - {str(e)}")
                    
                    last_run[test_name] = current_time
            
            # Wait before next cycle
            time.sleep(5)
            
        except KeyboardInterrupt:
            print(f"\n\nMonitoring stopped at {datetime.now().strftime('%H:%M:%S')}")
            break
        except Exception as e:
            print(f"\nMonitoring error: {e}")
            time.sleep(10)

def test_all_endpoints():
    """Test all endpoints once"""
    print("Testing all AnwaltsAI API endpoints")
    print("=" * 40)
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{BASE_URL}/health"
        },
        {
            "name": "Templates",
            "method": "GET", 
            "url": f"{BASE_URL}/api/templates"
        },
        {
            "name": "Sanitization",
            "method": "POST",
            "url": f"{BASE_URL}/api/sanitize",
            "data": {"text": "Email: test@example.com, Phone: +49 30 12345678, IBAN: DE89 3704 0044 0532 0130 00"}
        },
        {
            "name": "AI Response",
            "method": "POST",
            "url": f"{BASE_URL}/api/ai/respond", 
            "data": {"sanitized_text": "Ich benötige rechtliche Beratung.", "context": "Vertragsrecht"}
        }
    ]
    
    for test in tests:
        print(f"\n{test['name']}:")
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=10)
            else:
                response = requests.post(test["url"], json=test["data"], timeout=15)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if test["name"] == "Health Check":
                    print(f"  Service: {data.get('service')}")
                    print(f"  Components: {data.get('components')}")
                elif test["name"] == "Templates":
                    templates = data.get('templates', [])
                    print(f"  Templates available: {len(templates)}")
                    for template in templates:
                        print(f"    - {template['name']} ({template['category']})")
                elif test["name"] == "Sanitization":
                    print(f"  Entities removed: {len(data.get('entities_removed', []))}")
                    print(f"  Processing time: {data.get('processing_time')}s")
                    for entity in data.get('entities_removed', []):
                        print(f"    - {entity['type']}: {entity['original']} -> {entity['replacement']}")
                elif test["name"] == "AI Response":
                    print(f"  Response length: {len(data.get('ai_response', ''))} chars")
                    print(f"  Model used: {data.get('model_used')}")
                    print(f"  Processing time: {data.get('processing_time')}s")
            else:
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_api()
    else:
        test_all_endpoints()
        print(f"\nTo start real-time monitoring, run:")
        print(f"python monitor_logs.py monitor")