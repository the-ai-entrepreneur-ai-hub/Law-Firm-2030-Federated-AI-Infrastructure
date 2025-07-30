#!/usr/bin/env python3
"""
Comprehensive test of the trained German Legal AI model
"""

import sys
import os
sys.path.append('/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai/local-training/trained_model')

from deploy_model import AnwaltsAILocal

def test_model():
    """Test the model with different document types"""
    print("🧪 Testing Anwalts AI Local Model")
    print("=" * 50)
    
    model = AnwaltsAILocal()
    
    test_cases = [
        ("Klage", "Hiermit erheben wir Klage gegen Sie wegen ausstehender Zahlungen in Höhe von 5000 Euro."),
        ("Abmahnung", "Wir mahnen Sie hiermit ab wegen Verletzung unserer Markenrechte."),
        ("Kündigung", "Hiermit kündigen wir das Arbeitsverhältnis fristlos zum nächstmöglichen Zeitpunkt."),
        ("Mahnung", "Wir mahnen die ausstehende Rechnung vom 15.01.2024 in Höhe von 1500 Euro an."),
        ("Allgemein", "Wir benötigen eine rechtliche Stellungnahme zu diesem Sachverhalt.")
    ]
    
    for i, (doc_type, test_text) in enumerate(test_cases, 1):
        print(f"\n📄 Test {i}: {doc_type}")
        print(f"Input: {test_text[:60]}...")
        print("Response:")
        response = model.generate_response(test_text)
        print(response)
        print("-" * 40)
    
    print(f"\n✅ Model testing completed!")
    print(f"📊 Model Config:")
    print(f"   - Training Date: {model.config['training_date']}")
    print(f"   - Total Examples: {model.config['total_examples']}")
    print(f"   - Document Types: {list(model.config['document_types'].keys())}")

if __name__ == "__main__":
    test_model()