#!/usr/bin/env python3
"""
Model Selection Update for Anwalts AI
Adds local model integration to the existing secure_sanitizer.py
"""

from pathlib import Path

integration_code = '''
# =============================================================================
# LOCAL MODEL INTEGRATION - Add this section to secure_sanitizer.py
# =============================================================================

# Add after existing imports
import sys
from pathlib import Path

# Add local model integration
try:
    # Add path to local model
    local_model_path = Path(__file__).parent / "local-training" / "trained_model"
    sys.path.append(str(local_model_path))
    
    from deploy_model import AnwaltsAILocal
    local_ai = AnwaltsAILocal()
    LOCAL_MODEL_AVAILABLE = True
    print("✅ Local Anwalts AI model loaded successfully")
except Exception as e:
    LOCAL_MODEL_AVAILABLE = False
    print(f"⚠️ Local model not available: {e}")

# Local model processing function
def process_with_local_model(anonymized_text: str) -> Dict:
    """Process document with local model"""
    if not LOCAL_MODEL_AVAILABLE:
        return {"success": False, "error": "Local model not available"}
    
    try:
        result = local_ai.generate_response(anonymized_text)
        doc_type = local_ai._classify_document(anonymized_text)
        
        return {
            "success": True,
            "response": result,
            "model_used": "Anwalts AI Local v1.0",
            "confidence": 0.95,
            "document_type": doc_type,
            "processing_method": "local_training"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# =============================================================================
# NEW API ENDPOINTS - Add these routes to your Flask app
# =============================================================================

@app.route('/health-local', methods=['GET'])
def health_local():
    """Health check for local model"""
    if LOCAL_MODEL_AVAILABLE:
        try:
            # Test local model
            test_doc = "Test Klage wegen Gehaltszahlungen"
            result = process_with_local_model(test_doc)
            
            return jsonify({
                "status": "healthy" if result["success"] else "error",
                "model_info": {
                    "model_name": local_ai.config["model_name"],
                    "version": local_ai.config["version"],
                    "training_date": local_ai.config["training_date"],
                    "total_examples": local_ai.config["total_examples"],
                    "document_types": local_ai.config["document_types"]
                },
                "test_response": result.get("response", "")[:100] + "..." if result.get("response") else "",
                "last_check": datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }), 500
    else:
        return jsonify({
            "status": "unavailable", 
            "error": "Local model not loaded",
            "last_check": datetime.now().isoformat()
        }), 503

@app.route('/process-local', methods=['POST'])
def process_local():
    """Process document with local model only"""
    if not LOCAL_MODEL_AVAILABLE:
        return jsonify({"error": "Local model not available"}), 503
    
    try:
        data = request.json
        document_text = data.get('text', '')
        
        if not document_text:
            return jsonify({"error": "No document text provided"}), 400
            
        result = process_with_local_model(document_text)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/models', methods=['GET'])
def get_available_models():
    """Get available AI models"""
    models = [
        {
            "id": "together",
            "name": "Together AI (DeepSeek-V3)",
            "type": "cloud",
            "status": "available" if TOGETHER_API_KEY else "unavailable",
            "features": ["highest_accuracy", "complex_documents", "internet_required"],
            "description": "Advanced cloud-based AI processing"
        }
    ]
    
    if LOCAL_MODEL_AVAILABLE:
        models.append({
            "id": "local",
            "name": "Anwalts AI Local Model",
            "type": "local",
            "status": "available",
            "features": ["privacy_focused", "instant_response", "offline_capable"],
            "description": "Custom-trained German legal model",
            "training_info": {
                "examples": local_ai.config["total_examples"],
                "document_types": list(local_ai.config["document_types"].keys()),
                "training_date": local_ai.config["training_date"]
            }
        })
    else:
        models.append({
            "id": "local",
            "name": "Anwalts AI Local Model",
            "type": "local", 
            "status": "unavailable",
            "error": "Local model not loaded"
        })
    
    return jsonify({"models": models})

# =============================================================================
# ENHANCED PROCESS DOCUMENT ENDPOINT - Replace existing process_document
# =============================================================================

@app.route('/process-document', methods=['POST'])
def process_document_enhanced():
    """Enhanced document processing with model selection"""
    start_time = time.time()
    
    try:
        # Handle both file upload and JSON data
        if request.files:
            # File upload
            file = request.files.get('file')
            model_preference = request.form.get('model', 'together')
            
            if not file:
                return jsonify({"error": "No file provided"}), 400
                
            # Extract text from file
            extracted_text = extract_text_from_file(file)
            
        else:
            # JSON data
            data = request.json
            extracted_text = data.get('text', '')
            model_preference = data.get('model', 'together')
            
        if not extracted_text:
            return jsonify({"error": "No text to process"}), 400
        
        # PII Detection and anonymization
        pii_detector = PIIDetector()
        anonymized_text, pii_data = pii_detector.anonymize_document(extracted_text)
        
        # Process with selected model
        ai_result = None
        
        if model_preference == 'local' and LOCAL_MODEL_AVAILABLE:
            # Use local model
            ai_result = process_with_local_model(anonymized_text)
            model_used = "local"
        else:
            # Use Together AI (fallback or explicit choice)
            ai_result = process_with_together_ai(anonymized_text)
            model_used = "together"
        
        processing_time = time.time() - start_time
        
        # Prepare response
        response_data = {
            "success": True,
            "model_used": model_used,
            "processing_time": f"{processing_time:.2f}s",
            "original_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "anonymized_text": anonymized_text,
            "pii_data": [{"type": pii.type, "value": pii.original, "replacement": pii.replacement} for pii in pii_data],
            "pii_count": len(pii_data),
            "response": ai_result.get("response", "No response generated") if ai_result else "Processing failed",
            "confidence": ai_result.get("confidence", 0.5) if ai_result else 0.5,
            "document_type": ai_result.get("document_type", "Unknown") if ai_result else "Unknown",
            "analysis": ai_result.get("response", "") if ai_result else ""
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Document processing error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "processing_time": f"{time.time() - start_time:.2f}s"
        }), 500

def process_with_together_ai(anonymized_text: str) -> Dict:
    """Process with Together AI (existing function - modify if needed)"""
    try:
        client = Together(api_key=TOGETHER_API_KEY)
        
        # Optimize prompt for anonymized documents
        optimized_prompt = optimize_prompt_for_anonymized(anonymized_text)
        
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "Sie sind ein erfahrener deutscher Rechtsanwalt und erstellen professionelle rechtliche Antworten auf anonymisierte Dokumente."
                },
                {
                    "role": "user", 
                    "content": optimized_prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "success": True,
            "response": ai_response,
            "model_used": "Together AI (DeepSeek-V3)",
            "confidence": 0.9,
            "document_type": "Legal Document",
            "processing_method": "cloud_api"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_text_from_file(file):
    """Extract text from uploaded file - modify your existing function"""
    # Your existing text extraction logic here
    # This should return the extracted text from PDF, DOCX, or other formats
    pass

# =============================================================================
# ENHANCED HEALTH CHECK - Update existing health endpoint
# =============================================================================

@app.route('/health', methods=['GET'])
def health_enhanced():
    """Enhanced health check including model status"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "together_ai": {
                "status": "available" if TOGETHER_API_KEY else "unavailable",
                "model": LLM_MODEL_NAME
            },
            "local_model": {
                "status": "available" if LOCAL_MODEL_AVAILABLE else "unavailable"
            }
        },
        "features": [
            "pii_detection",
            "german_legal_processing", 
            "multi_format_support"
        ]
    }
    
    if LOCAL_MODEL_AVAILABLE:
        health_data["models"]["local_model"].update({
            "name": local_ai.config["model_name"],
            "version": local_ai.config["version"], 
            "training_examples": local_ai.config["total_examples"]
        })
    
    return jsonify(health_data)
'''

def main():
    """Generate the integration code and instructions"""
    print("🔧 Anwalts AI Model Selection Integration")
    print("=" * 60)
    
    # Save integration code
    base_dir = Path("/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai")
    integration_file = base_dir / "model_integration_code.py"
    
    with open(integration_file, 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    print(f"✅ Integration code saved to: {integration_file}")
    print()
    print("📋 Integration Steps:")
    print("1. Copy the code sections from model_integration_code.py")
    print("2. Add them to your secure_sanitizer.py file")
    print("3. Replace the original pii_interface.html with enhanced_pii_interface.html")
    print("4. Restart your Docker container:")
    print("   docker restart law-firm-ai-optimized")
    print()
    print("🚀 New Features After Integration:")
    print("• Model selection in web interface (Together AI vs Local)")
    print("• Health checks for both models (/health-local)")
    print("• Enhanced processing endpoint with model choice")
    print("• Model capabilities API (/models)")
    print("• Local-only processing endpoint (/process-local)")
    print()
    print("🌐 New API Endpoints:")
    print("• GET /health-local - Local model health")
    print("• GET /models - Available models info")
    print("• POST /process-local - Local model only")
    print("• POST /process-document - Enhanced with model selection")
    print()
    print("✅ Ready to enhance your Anwalts AI system!")

if __name__ == "__main__":
    main()