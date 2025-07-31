#!/usr/bin/env python3
"""
Test script to verify PII placeholder replacement is working correctly
"""
import requests
import json

# Test the placeholder replacement function directly
def test_placeholder_replacement():
    """Test the placeholder replacement function"""
    from simple_fastapi_backend import replace_placeholders_with_natural_language
    
    test_text = """
    Sehr geehrte [PER_1],
    
    hiermit bestätigen wir den Eingang Ihrer Nachricht bezüglich [AKTENZEICHEN_1].
    
    Bitte überweisen Sie den Betrag auf das Konto [IBAN_1] mit der Steuernummer [STEUER_ID_1].
    
    Kontaktieren Sie uns unter [PHONE_1] oder per E-Mail an [EMAIL_1].
    
    Ihre Adresse [PLZ_1] [LOC_1] wurde in unserer Datenbank hinterlegt.
    
    Mit freundlichen Grüßen
    [ORG_1]
    """
    
    print("=== ORIGINAL TEXT WITH PII PLACEHOLDERS ===")
    print(test_text)
    
    cleaned = replace_placeholders_with_natural_language(test_text)
    
    print("\n=== CLEANED TEXT (PLACEHOLDERS REPLACED) ===")
    print(cleaned)
    
    print("\n=== ANALYSIS ===")
    if "[" in cleaned and "]" in cleaned:
        print("WARNING: Some placeholders may still remain!")
    else:
        print("SUCCESS: All placeholders have been replaced with natural language")

# Test the API endpoint
def test_api_sanitize():
    """Test the sanitization API endpoint"""
    print("\n" + "="*60)
    print("TESTING API SANITIZATION ENDPOINT")
    print("="*60)
    
    test_text = """
    Sehr geehrter Herr Müller,
    
    bezüglich Ihrer Anfrage vom 15.01.2024 zu Aktenzeichen 123 AG 456/24
    teilen wir Ihnen mit, dass die Zahlung von 5.000 EUR auf das Konto
    DE89 3704 0044 0532 0130 00 erfolgen sollte.
    
    Ihre Steuernummer 12 345 678 901 wurde in unserem System hinterlegt.
    
    Bei Fragen erreichen Sie uns unter +49 30 12345678 oder per E-Mail
    an kanzlei@example.de.
    
    Mit freundlichen Grüßen
    Rechtsanwaltskanzlei Schmidt & Partner
    """
    
    try:
        response = requests.post(
            "http://localhost:8003/api/sanitize",
            json={"text": test_text},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("API Response successful")
            print(f"Entities removed: {len(data['entities_removed'])}")
            print(f"Processing time: {data['processing_time']}s")
            
            print("\n--- SANITIZED TEXT ---")
            print(data['sanitized_text'])
            
            print("\n--- ENTITIES REMOVED ---")
            for entity in data['entities_removed']:
                print(f"  * {entity['type']}: {entity['original']} -> {entity['replacement']}")
                
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")
        print("Make sure the server is running on http://localhost:8003")

if __name__ == "__main__":
    print("TESTING PII PLACEHOLDER REPLACEMENT FIX")
    print("="*60)
    
    test_placeholder_replacement()
    test_api_sanitize()
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("The server should now replace PII placeholders with natural German terms")
    print("before sending text to the AI model, preventing information leakage.")