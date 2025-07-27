#!/usr/bin/env python3
"""
Test script for the trained Anwalts AI local model
"""

import sys
import os

# Add the model directory to path
sys.path.append('/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai/local-training/trained_model')

from deploy_model import AnwaltsAILocal

def test_model():
    """Test the trained model with various document types"""
    
    print("🧪 Testing Anwalts AI Local Model")
    print("=" * 50)
    
    model = AnwaltsAILocal()
    
    # Test cases for different document types
    test_cases = [
        {
            "name": "Klage Test",
            "document": """
            Klageerhebung wegen ausstehender Gehaltszahlungen
            
            Sehr geehrte Damen und Herren,
            
            in der Angelegenheit [PERSON_NAME_1] gegen [COMPANY_1] erheben wir Klage 
            wegen ausstehender Gehaltszahlungen in Höhe von [AMOUNT_1] Euro.
            
            Unser Mandant hat seit drei Monaten kein Gehalt erhalten.
            """
        },
        {
            "name": "Abmahnung Test", 
            "document": """
            Abmahnung wegen Urheberrechtsverletzung
            
            Sehr geehrte Damen und Herren,
            
            Sie haben auf Ihrer Website [WEBSITE_1] ein Bild verwendet, 
            an dem unsere Mandantin die ausschließlichen Nutzungsrechte besitzt.
            
            Wir fordern Sie auf, das Bild zu entfernen.
            """
        },
        {
            "name": "Kündigung Test",
            "document": """
            Kündigung des Arbeitsverhältnisses
            
            Sehr geehrte/r [PERSON_NAME_1],
            
            hiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis 
            fristgerecht zum [DATE_1].
            
            Die Kündigung erfolgt aus betriebsbedingten Gründen.
            """
        },
        {
            "name": "Mahnung Test",
            "document": """
            Zahlungserinnerung
            
            Sehr geehrte Damen und Herren,
            
            wir mahnen Sie hiermit zur Zahlung der offenen Rechnung 
            Nr. [INVOICE_1] in Höhe von [AMOUNT_1] Euro an.
            
            Die Zahlung ist seit [DATE_1] überfällig.
            """
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📄 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        print("Input Document:")
        print(test_case['document'])
        
        print("\nGenerated Response:")
        response = model.generate_response(test_case['document'])
        print(response)
        
        print("\n" + "="*50)
    
    # Test model configuration
    print(f"\n📊 Model Statistics:")
    print(f"Model Name: {model.config['model_name']}")
    print(f"Version: {model.config['version']}")
    print(f"Training Date: {model.config['training_date']}")
    print(f"Total Examples: {model.config['total_examples']}")
    
    print(f"\nDocument Types Trained:")
    for doc_type, count in model.config['document_types'].items():
        print(f"  {doc_type}: {count} examples")
    
    print(f"\n✅ Model testing completed successfully!")

if __name__ == "__main__":
    test_model()