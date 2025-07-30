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

class TestNDAGeneration(unittest.TestCase):

    def setUp(self):
        """Set up the test case."""
        self.model = AnwaltsAILocal()
        self.prompt = "Erstellen Sie eine Geheimhaltungsvereinbarung (NDA) für das Projekt 'Lawyer AI' zwischen den Projekteigentümern und dem Entwickler Christopher."

    def test_nda_generation(self):
        """Test that the model can generate the specific NDA."""
        print("\n" + "="*50)
        print("         NDA GENERATION TEST")
        print("="*50 + "\n")
        
        response = self.model.generate_response(self.prompt)
        
        # Check for key phrases in the generated NDA
        self.assertIn("Geheimhaltungsvereinbarung (NDA)", response)
        self.assertIn("Projekt 'Lawyer AI'", response)
        self.assertIn("Herrn Christopher", response)
        self.assertIn("Geheimnisgeber", response)
        self.assertIn("Geheimnisempfänger", response)
        self.assertIn("Vertragsstrafe", response)
        
        print("--- TEST PASSED ---")
        print("Model successfully generated the NDA with all key elements.")
        print("\n--- Generated NDA ---")
        print(response)
        print("="*50)

if __name__ == "__main__":
    unittest.main()
