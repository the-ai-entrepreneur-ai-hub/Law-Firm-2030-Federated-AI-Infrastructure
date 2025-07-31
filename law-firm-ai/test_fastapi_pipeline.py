#!/usr/bin/env python3
"""
Test Script for AnwaltsAI FastAPI Pipeline
Tests all major endpoints and functionality
"""

import asyncio
import json
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_sanitize_endpoint():
    """Test PII sanitization endpoint"""
    print("\n🔒 Testing PII sanitization...")
    
    test_text = """
    Sehr geehrte Damen und Herren,
    
    hiermit wende ich mich an Sie bezüglich des Mandanten Hans Schmidt, 
    geboren am 15.03.1985, wohnhaft in der Hauptstraße 45, 12345 Musterstadt.
    
    Die Telefonnummer des Mandanten lautet +49 30 12345678.
    E-Mail: hans.schmidt@email.de
    IBAN: DE89 3704 0044 0532 0130 00
    Steuer-ID: 12 345 678 901
    
    Mit freundlichen Grüßen
    Dr. Anna Müller
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/sanitize",
            json={"text": test_text}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sanitization successful")
            print(f"   Entities removed: {len(data['entities_removed'])}")
            print(f"   Processing time: {data['processing_time']}s")
            
            # Show first few entities
            for i, entity in enumerate(data['entities_removed'][:3]):
                print(f"   • {entity['type']}: {entity['detection_method']} (confidence: {entity['confidence']})")
            
            return data['sanitized_text']
        else:
            print(f"❌ Sanitization failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Sanitization error: {e}")
        return None

def test_ai_response_endpoint(sanitized_text=None):
    """Test AI response generation"""
    print("\n🤖 Testing AI response generation...")
    
    if not sanitized_text:
        sanitized_text = "Sehr geehrte Damen und Herren, ich benötige rechtliche Beratung bezüglich eines Vertrags."
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/respond",
            json={
                "sanitized_text": sanitized_text,
                "context": "Vertragsrecht",
                "document_type": "general",
                "temperature": 0.1
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI response generated")
            print(f"   Model used: {data['model_used']}")
            print(f"   Processing time: {data['processing_time']}s")
            print(f"   Tokens used: {data.get('tokens_used', 'N/A')}")
            print(f"   Response preview: {data['ai_response'][:100]}...")
            return True
        else:
            print(f"❌ AI response failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI response error: {e}")
        return False

def test_templates_endpoint():
    """Test templates endpoint"""
    print("\n📋 Testing templates endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/templates")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            print(f"✅ Templates retrieved: {len(templates)} available")
            
            for template in templates:
                print(f"   • {template['name']} ({template['category']})")
            
            return templates
        else:
            print(f"❌ Templates failed: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Templates error: {e}")
        return []

def test_generate_endpoint():
    """Test complete document generation"""
    print("\n📄 Testing document generation...")
    
    test_request = {
        "text": "Ich benötige eine Mahnung für eine überfällige Rechnung über 1.500 EUR von einem Kunden, der seit 30 Tagen nicht gezahlt hat.",
        "context": "Zahlungsverzug, erste Mahnung",
        "document_type": "mahnung"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json=test_request
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document generation successful")
            print(f"   Processing time: {data['processing_stats']['processing_time']}s")
            print(f"   Input length: {data['processing_stats']['input_length']} chars")
            print(f"   Output length: {data['processing_stats']['output_length']} chars")
            print(f"   Entities removed: {data['processing_stats']['entities_removed']}")
            print(f"   Download URL: {data.get('download_url', 'N/A')}")
            print(f"   Document preview: {data['generated_doc'][:200]}...")
            return True
        else:
            print(f"❌ Document generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document generation error: {e}")
        return False

def test_server_connectivity():
    """Test if server is running"""
    print("🔌 Testing server connectivity...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Run all tests"""
    print("🧪 AnwaltsAI FastAPI Pipeline Tests")
    print("=" * 50)
    
    # Check if server is running
    if not test_server_connectivity():
        print("❌ Server not reachable!")
        print("   Make sure the FastAPI server is running:")
        print("   python start_fastapi_server.py")
        return
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: PII Sanitization
    sanitized_text = test_sanitize_endpoint()
    if sanitized_text:
        tests_passed += 1
    
    # Test 3: AI Response Generation
    if test_ai_response_endpoint(sanitized_text):
        tests_passed += 1
    
    # Test 4: Templates
    templates = test_templates_endpoint()
    if templates:
        tests_passed += 1
    
    # Test 5: Document Generation
    if test_generate_endpoint():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! The AnwaltsAI backend is ready for React integration.")
        print("\n🔗 Frontend Integration URLs:")
        print(f"   • Upload API: {BASE_URL}/api/upload")
        print(f"   • Sanitize API: {BASE_URL}/api/sanitize")
        print(f"   • AI Response API: {BASE_URL}/api/ai/respond")
        print(f"   • Generate API: {BASE_URL}/api/generate")
        print(f"   • Templates API: {BASE_URL}/api/templates")
    else:
        print(f"⚠️  Some tests failed. Check server logs and environment.")
    
    print("\n📚 API Documentation available at:")
    print(f"   • Swagger UI: {BASE_URL}/docs")
    print(f"   • ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()