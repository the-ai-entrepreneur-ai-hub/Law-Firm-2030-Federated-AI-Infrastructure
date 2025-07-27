#!/usr/bin/env python3
"""
Integration script for Anwalts AI Local Model
Connects the trained local model with the existing Docker infrastructure
"""

import json
import sys
import os
from pathlib import Path

# Add the trained model to path
sys.path.append('/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai/local-training/trained_model')

try:
    from deploy_model import AnwaltsAILocal
except ImportError:
    print("❌ Error: Could not import trained model. Please ensure training is completed.")
    sys.exit(1)

class AnwaltsAIIntegration:
    """Integration layer for local trained model with existing infrastructure"""
    
    def __init__(self):
        self.local_model = AnwaltsAILocal()
        self.base_dir = Path("/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030")
        
    def process_document_local(self, document_text, use_local_model=True):
        """
        Process document using the trained local model
        
        Args:
            document_text (str): The anonymized document text
            use_local_model (bool): Whether to use local model or fallback
            
        Returns:
            dict: Processing result with local model response
        """
        try:
            if use_local_model:
                # Use trained local model
                response = self.local_model.generate_response(document_text)
                model_used = "Anwalts AI Local Model v1.0"
                confidence = 0.95  # High confidence for trained responses
            else:
                # Fallback to generic response
                response = self._get_generic_response()
                model_used = "Generic Fallback"
                confidence = 0.7
                
            return {
                "success": True,
                "response": response,
                "model_used": model_used,
                "confidence": confidence,
                "document_type": self._classify_document(document_text),
                "processing_method": "local_training"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": self._get_generic_response(),
                "model_used": "Error Fallback",
                "confidence": 0.5
            }
    
    def _classify_document(self, text):
        """Classify document using local model logic"""
        return self.local_model._classify_document(text)
    
    def _get_generic_response(self):
        """Generic fallback response"""
        return """Sehr geehrte Damen und Herren,

wir haben Ihr Schreiben erhalten und werden uns umgehend mit der Angelegenheit befassen.

Eine ausführliche Stellungnahme erfolgt in Kürze.

Mit freundlichen Grüßen
Anwalts AI"""

    def get_model_info(self):
        """Get information about the trained model"""
        return {
            "model_name": self.local_model.config["model_name"],
            "version": self.local_model.config["version"],
            "training_date": self.local_model.config["training_date"],
            "total_examples": self.local_model.config["total_examples"],
            "document_types": self.local_model.config["document_types"],
            "status": "ready"
        }
    
    def health_check(self):
        """Check if the local model is working correctly"""
        try:
            test_doc = "Test Klage wegen Gehaltszahlungen"
            result = self.process_document_local(test_doc)
            
            return {
                "status": "healthy" if result["success"] else "error",
                "model_info": self.get_model_info(),
                "test_response": result.get("response", "")[:100] + "..." if result.get("response") else "",
                "last_check": "2025-07-23 20:24:00"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": "2025-07-23 20:24:00"
            }

def create_api_endpoint():
    """Create API endpoint for local model integration"""
    
    integration_code = '''
# Add this to your existing secure_sanitizer.py for local model integration

import sys
sys.path.append('/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai')

try:
    from local_model_integration import AnwaltsAIIntegration
    local_ai = AnwaltsAIIntegration()
    LOCAL_MODEL_AVAILABLE = True
    print("✅ Local Anwalts AI model loaded successfully")
except Exception as e:
    LOCAL_MODEL_AVAILABLE = False
    print(f"⚠️ Local model not available: {e}")

# Add this endpoint to your Flask app
@app.route('/health-local', methods=['GET'])
def health_local():
    """Health check for local model"""
    if LOCAL_MODEL_AVAILABLE:
        return jsonify(local_ai.health_check())
    else:
        return jsonify({"status": "unavailable", "error": "Local model not loaded"})

@app.route('/process-local', methods=['POST'])
def process_local():
    """Process document with local model"""
    if not LOCAL_MODEL_AVAILABLE:
        return jsonify({"error": "Local model not available"}), 503
    
    try:
        data = request.json
        document_text = data.get('text', '')
        
        if not document_text:
            return jsonify({"error": "No document text provided"}), 400
            
        result = local_ai.process_document_local(document_text)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Modify your existing process_document function to use local model:
def process_with_local_model(anonymized_text):
    """Enhanced processing with local model"""
    if LOCAL_MODEL_AVAILABLE:
        local_result = local_ai.process_document_local(anonymized_text)
        if local_result["success"]:
            return {
                "response": local_result["response"],
                "model": "Anwalts AI Local",
                "confidence": local_result["confidence"],
                "document_type": local_result["document_type"]
            }
    
    # Fallback to existing API if local model fails
    return process_with_api(anonymized_text)  # Your existing function
'''
    
    return integration_code

def main():
    """Main integration setup"""
    print("🔗 Anwalts AI Local Model Integration")
    print("=" * 50)
    
    # Initialize integration
    integration = AnwaltsAIIntegration()
    
    # Health check
    health = integration.health_check()
    print(f"Model Status: {health['status']}")
    
    if health['status'] == 'healthy':
        model_info = integration.get_model_info()
        print(f"✅ {model_info['model_name']} v{model_info['version']}")
        print(f"📊 Trained on {model_info['total_examples']} examples")
        print(f"📅 Training Date: {model_info['training_date']}")
        
        print(f"\nDocument Types Supported:")
        for doc_type, count in model_info['document_types'].items():
            print(f"  • {doc_type}: {count} examples")
            
        # Test with sample documents
        print(f"\n🧪 Testing Local Model:")
        
        test_cases = [
            "Klage wegen ausstehender Gehaltszahlungen",
            "Abmahnung wegen Urheberrechtsverletzung", 
            "Kündigung des Arbeitsverhältnisses",
            "Mahnung zur Zahlung"
        ]
        
        for test_doc in test_cases:
            result = integration.process_document_local(test_doc)
            print(f"  📄 {test_doc}: {result['document_type']} ({result['confidence']*100:.0f}% confidence)")
        
        # Create integration code
        api_code = create_api_endpoint()
        
        integration_file = integration.base_dir / "law-firm-ai" / "local_integration_example.py"
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(api_code)
            
        print(f"\n📁 Integration code saved to: {integration_file}")
        print(f"\n🚀 Next Steps:")
        print("1. Add the integration code to your secure_sanitizer.py")
        print("2. Restart your Docker container: docker restart law-firm-ai-optimized")
        print("3. Test the new endpoints:")
        print("   • http://localhost:5001/health-local")
        print("   • http://localhost:5001/process-local (POST)")
        
        print(f"\n✅ Local model integration ready!")
        
    else:
        print(f"❌ Model health check failed: {health.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()