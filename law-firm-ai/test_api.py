#!/usr/bin/env python3
"""
Test script to verify Together AI API connection and model availability.
"""

import sys
import os

# Test if together library is available
try:
    from together import Together
    print("✓ Together AI library is available")
except ImportError:
    print("✗ Together AI library is not installed")
    print("Please install with: pip install together")
    sys.exit(1)

# Test API connection
TOGETHER_API_KEY = "REDACTED"

try:
    client = Together(api_key=TOGETHER_API_KEY)
    print("✓ Together AI client initialized")
except Exception as e:
    print(f"✗ Failed to initialize Together AI client: {e}")
    sys.exit(1)

# Test API connectivity
try:
    # List available models
    models = client.models.list()
    print(f"✓ API connection successful. Found {len(models)} models")
    
    # Check for DeepSeek models
    deepseek_models = [model for model in models if 'deepseek' in model.id.lower()]
    print(f"✓ Found {len(deepseek_models)} DeepSeek models")
    
    for model in deepseek_models:  # Show all DeepSeek models
        print(f"  - {model.id}")
    
except Exception as e:
    print(f"✗ API connection failed: {e}")
    # Try a simple chat completion instead
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-1B-Instruct-Turbo",
            messages=[{"role": "user", "content": "Hello, world!"}],
            max_tokens=10
        )
        print("✓ Basic API test successful")
    except Exception as e2:
        print(f"✗ Basic API test also failed: {e2}")
        sys.exit(1)

# Test fine-tuning capabilities
try:
    # Try to access fine-tuning API - check what methods are available
    print(f"Fine-tuning object methods: {dir(client.fine_tuning)}")
    
    # Try different ways to access fine-tuning
    if hasattr(client.fine_tuning, 'list'):
        jobs = client.fine_tuning.list()
        print("✓ Fine-tuning API access available (direct list)")
    elif hasattr(client, 'fine_tunes'):
        jobs = client.fine_tunes.list()
        print("✓ Fine-tuning API access available (fine_tunes)")
    else:
        print("⚠ Fine-tuning API structure unclear")
        
except Exception as e:
    print(f"⚠ Fine-tuning API access issue: {e}")

# Test if DeepSeek-V3 is available specifically
print("\nTesting DeepSeek-V3 availability...")
try:
    # Check if the exact model from training script is available
    target_model = "deepseek-ai/DeepSeek-V3"
    available_models = [model.id for model in models]
    
    if target_model in available_models:
        print(f"✓ {target_model} is available for inference")
    else:
        print(f"✗ {target_model} is not available")
        # Look for similar models
        v3_models = [m for m in available_models if 'deepseek' in m.lower() and 'v3' in m.lower()]
        if v3_models:
            print(f"Available DeepSeek V3 variants: {v3_models}")
        else:
            print("No DeepSeek V3 models found")

except Exception as e:
    print(f"Error checking model availability: {e}")

print("\nAPI test completed!")