#!/usr/bin/env python3
"""
Debug Together.ai integration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def test_together_ai():
    print("=" * 50)
    print("Together.ai Integration Debug")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        print(f"[OK] API Key found: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("[ERROR] API Key not found")
        return
    
    # Test import
    try:
        from together import Together
        print("[OK] Together.ai library imported successfully")
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return
    
    # Test client initialization
    try:
        client = Together(api_key=api_key)
        print("[OK] Together.ai client created successfully")
    except Exception as e:
        print(f"[ERROR] Client creation error: {e}")
        return
    
    # Test simple API call
    try:
        print("\nTesting API call...")
        messages = [
            {"role": "system", "content": "Du bist ein deutscher Rechtsanwalt. Antworte auf Deutsch."},
            {"role": "user", "content": "Erstelle eine kurze Mahnung für eine überfällige Rechnung."}
        ]
        
        # Try different models
        models_to_try = [
            "meta-llama/Llama-3.1-70B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "meta-llama/Llama-3-70b-chat-hf",
            "meta-llama/Meta-Llama-3-70B-Instruct",
            "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
        ]
        
        for model in models_to_try:
            try:
                print(f"Trying model: {model}")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.1
                )
                print(f"[SUCCESS] Model {model} works!")
                break
            except Exception as e:
                print(f"[FAILED] Model {model}: {e}")
                continue
        else:
            print("[ERROR] No working models found")
            return False
        
        if response and response.choices:
            content = response.choices[0].message.content
            print("[SUCCESS] API call successful!")
            print(f"Response length: {len(content)} characters")
            print(f"Preview: {content[:200]}...")
            return True
        else:
            print("[ERROR] Empty response from API")
            return False
            
    except Exception as e:
        print(f"[ERROR] API call error: {e}")
        return False

if __name__ == "__main__":
    success = test_together_ai()
    if success:
        print("\n[SUCCESS] Together.ai integration is working!")
    else:
        print("\n[ERROR] Together.ai integration has issues.")