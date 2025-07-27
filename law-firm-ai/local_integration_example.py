
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
