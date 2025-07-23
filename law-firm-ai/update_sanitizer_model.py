#!/usr/bin/env python3
"""
Script to update sanitizer_app.py with the trained model ID.
"""

import json
import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_model_in_sanitizer():
    """Update the sanitizer with the trained model ID."""
    
    # Check if model info exists
    model_info_path = "trained_model_info.json"
    if not os.path.exists(model_info_path):
        logger.error("trained_model_info.json not found. Run train_model.py first.")
        return False
    
    # Load model info
    with open(model_info_path, 'r') as f:
        model_info = json.load(f)
    
    trained_model_id = model_info.get('model_id')
    if not trained_model_id:
        logger.error("No model_id found in trained_model_info.json")
        return False
    
    logger.info(f"Found trained model ID: {trained_model_id}")
    
    # Read current sanitizer
    sanitizer_path = "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai/sanitizer_app.py"
    with open(sanitizer_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the model name
    old_pattern = r'LLM_MODEL_NAME = "deepseek-ai/DeepSeek-V3"'
    new_model_line = f'LLM_MODEL_NAME = "{trained_model_id}"'
    
    if old_pattern in content:
        updated_content = re.sub(old_pattern, new_model_line, content)
        
        # Write back the updated content
        with open(sanitizer_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"Updated sanitizer_app.py with trained model: {trained_model_id}")
        return True
    else:
        logger.error("Could not find model configuration line in sanitizer_app.py")
        return False

if __name__ == "__main__":
    update_model_in_sanitizer()