#!/usr/bin/env python3
"""
Test Kimi model directly
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def test_kimi_model():
    print("Testing Kimi model directly...")
    
    # Test the user's exact example
    try:
        from together import Together
        
        client = Together()
        
        response = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": "What are some fun things to do in New York?"
                }
            ]
        )
        print("SUCCESS with user's example!")
        print(f"Response: {response.choices[0].message.content[:200]}...")
        
    except Exception as e:
        print(f"FAILED with user's example: {e}")
        return False
    
    # Test German legal prompt
    try:
        response = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein erfahrener deutscher Rechtsanwalt. Erstelle professionelle deutsche Rechtsdokumente."
                },
                {
                    "role": "user", 
                    "content": "Erstelle eine Geheimhaltungsvereinbarung (NDA) zwischen George (Entwickler) und Chris (Kunde) für ein Anwalts-KI-Projekt."
                }
            ]
        )
        print("\nSUCCESS with German legal prompt!")
        print(f"Response length: {len(response.choices[0].message.content)}")
        print(f"Preview: {response.choices[0].message.content[:300]}...")
        return True
        
    except Exception as e:
        print(f"FAILED with German legal prompt: {e}")
        return False

if __name__ == "__main__":
    success = test_kimi_model()
    if success:
        print("\n[SUCCESS] Kimi model is working for German legal documents!")
    else:
        print("\n[ERROR] Kimi model has issues.")