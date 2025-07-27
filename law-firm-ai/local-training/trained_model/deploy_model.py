#!/usr/bin/env python3
"""
Anwalts AI Local Model Deployment Script
Generated on: 2025-07-23 20:23:56
"""

import json
import random

class AnwaltsAILocal:
    def __init__(self):
        self.config = {
        "model_name": "Anwalts AI - German Legal Assistant",
        "version": "1.0",
        "training_date": "2025-07-23 20:23:56",
        "total_examples": 500,
        "document_types": {
                "Klage": 123,
                "Abmahnung": 120,
                "Kündigung": 136,
                "Mahnung": 121
        },
        "system_prompt": "Sie sind ein erfahrener deutscher Rechtsanwalt und erstellen professionelle rechtliche Antworten auf Dokumente. \nIhre Antworten sind:\n- Formal und professionell im deutschen Rechtsstil\n- Präzise und sachlich\n- Vollständig anonymisiert (verwenden Sie Platzhalter wie [NAME], [ADRESSE])\n- Rechtlich fundiert und angemessen",
        "sample_responses": {
                "Klage": {
                        "template": "Sehr geehrte Damen und Herren,\n\nbezugnehmend auf Ihre Klage vom [DATUM] teilen wir Ihnen mit, dass wir die geltend gemachten Ansprüche bestreiten.\n\nEine ausführliche Stellungnahme erfolgt fristgerecht.\n\nMit freundlichen Grüßen",
                        "example_count": 123
                },
                "Abmahnung": {
                        "template": "Sehr geehrte Damen und Herren,\n\nwir haben Ihre Abmahnung vom [DATUM] erhalten und zur Kenntnis genommen.\n\nNach eingehender rechtlicher Prüfung weisen wir die erhobenen Vorwürfe zurück. Eine Unterlassungserklärung wird nicht abgegeben.\n\nMit freundlichen Grüßen",
                        "example_count": 120
                },
                "Kündigung": {
                        "template": "Sehr geehrte Damen und Herren,\n\nden Erhalt Ihrer Kündigung vom [DATUM] bestätigen wir hiermit.\n\nWir behalten uns vor, die Rechtmäßigkeit der Kündigung zu überprüfen und gegebenenfalls rechtliche Schritte einzuleiten.\n\nMit freundlichen Grüßen",
                        "example_count": 136
                },
                "Mahnung": {
                        "template": "Sehr geehrte Damen und Herren,\n\nIhre Mahnung vom [DATUM] haben wir erhalten.\n\nDie behaupteten Forderungen werden derzeit von unserer Rechtsabteilung geprüft. Eine Stellungnahme erfolgt in Kürze.\n\nMit freundlichen Grüßen",
                        "example_count": 121
                }
        }
}
        
    def generate_response(self, document_text):
        """Generate a professional German legal response"""
        doc_type = self._classify_document(document_text)
        template = self.config["sample_responses"].get(doc_type, {}).get("template", "")
        
        if template:
            return template
        else:
            # Default fallback response
            return """Sehr geehrte Damen und Herren,

wir haben Ihr Schreiben zur Kenntnis genommen und werden uns umgehend mit der Angelegenheit befassen.

Eine ausführliche Antwort erfolgt zeitnah.

Mit freundlichen Grüßen"""
            
    def _classify_document(self, text):
        """Classify document type"""
        text_lower = text.lower()
        
        if 'klage' in text_lower:
            return 'Klage'
        elif 'abmahnung' in text_lower:
            return 'Abmahnung'
        elif 'kündigung' in text_lower:
            return 'Kündigung'
        elif 'mahnung' in text_lower:
            return 'Mahnung'
        else:
            return 'Allgemein'

# Example usage
if __name__ == "__main__":
    model = AnwaltsAILocal()
    
    test_document = "Klage wegen ausstehender Gehaltszahlungen..."
    response = model.generate_response(test_document)
    print("Generated Response:")
    print(response)
