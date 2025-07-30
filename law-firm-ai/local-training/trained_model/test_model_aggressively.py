import unittest
import sys
from pathlib import Path

# Add the model's directory to the Python path
model_dir = Path(__file__).parent.resolve()
sys.path.append(str(model_dir))

try:
    from deploy_model import AnwaltsAILocal
except ImportError:
    print("Error: Could not import AnwaltsAILocal from deploy_model.py.")
    print("Please ensure deploy_model.py is in the same directory.")
    sys.exit(1)

class TestAnwaltsAILocal(unittest.TestCase):

    def setUp(self):
        """Set up the test cases."""
        self.model = AnwaltsAILocal()
        self.test_cases = [
            # 1. Klage (Lawsuit)
            {"text": "An das Gericht: Klage wegen ausstehender Gehaltszahlungen.", "expected_type": "Klage"},
            
            # 2. Abmahnung (Warning)
            {"text": "Hiermit erhalten Sie eine Abmahnung wegen Urheberrechtsverletzung.", "expected_type": "Abmahnung"},
            
            # 3. Kündigung (Termination)
            {"text": "Außerordentliche Kündigung des Mietverhältnisses.", "expected_type": "Kündigung"},
            
            # 4. Mahnung (Dunning Reminder)
            {"text": "Letzte Mahnung: Offene Rechnung Nr. 12345.", "expected_type": "Mahnung"},
            
            # 5. Mahnung vs. Abmahnung (Edge Case)
            {"text": "Dies ist eine Abmahnung und gleichzeitig die letzte Mahnung.", "expected_type": "Abmahnung"},
            
            # 6. Vertrag (Contract)
            {"text": "Mietvertrag zwischen Mieter und Vermieter.", "expected_type": "Vertrag"},
            
            # 7. Allgemein (General) - No keywords
            {"text": "Sehr geehrte Damen und Herren, anbei erhalten Sie die gewünschten Unterlagen.", "expected_type": "Allgemein"},
            
            # 8. Klageschrift (Alternative keyword for Lawsuit)
            {"text": "Einreichung der Klageschrift beim Amtsgericht.", "expected_type": "Klage"},
            
            # 9. Case-insensitivity test
            {"text": "Wir erheben KLAGE.", "expected_type": "Klage"},
            
            # 10. Complex document text
            {"text": "In dem Rechtsstreit zwischen der Bau-GmbH und der Klägerin wird hiermit eine Klage eingereicht, die eine Abmahnung des Beklagten zum Gegenstand hat.", "expected_type": "Klage"},
            
            # 11. Noisy text with keyword
            {"text": "Der Bericht erwähnt eine Kündigung am Rande, aber der Hauptfokus ist die Jahresbilanz.", "expected_type": "Kündigung"},
            
            # 12. German special characters
            {"text": "Kündigung wegen übermäßiger Nutzung der Gemeinschaftsräume.", "expected_type": "Kündigung"},
        ]

    def test_document_classification(self):
        """Test the classification of various legal documents."""
        print("\n" + "="*50)
        print("      AGGRESSIVE MODEL CLASSIFICATION TEST")
        print("="*50 + "\n")
        
        success_count = 0
        
        for i, case in enumerate(self.test_cases):
            input_text = case["text"]
            expected = case["expected_type"]
            
            actual = self.model._classify_document(input_text)
            
            is_correct = (actual == expected)
            if is_correct:
                success_count += 1
                status = "PASSED"
            else:
                status = "FAILED"
            
            print(f"--- Test Case {i+1}: {status} ---")
            print(f"  Input:    '{input_text[:50]}...' ")
            print(f"  Expected: {expected}")
            print(f"  Actual:   {actual}")
            print("-"*(25 + len(status)))

        print("\n" + "="*50)
        print("                 TEST SUMMARY")
        print("="*50)
        print(f"  Total Tests: {len(self.test_cases)}")
        print(f"  Passed:      {success_count}")
        print(f"  Failed:      {len(self.test_cases) - success_count}")
        print(f"  Success Rate: {(success_count / len(self.test_cases)) * 100:.2f}%")
        print("="*50)

        self.assertEqual(success_count, len(self.test_cases), "Not all classification tests passed.")

if __name__ == "__main__":
    unittest.main()
