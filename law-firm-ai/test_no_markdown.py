#!/usr/bin/env python3
"""
Test that the AI no longer generates Markdown formatting
"""

import requests
import json

def test_no_markdown():
    url = "http://localhost:8003/api/generate"
    
    data = {
        "text": "I need a professional German contract for website development services between TechCorp GmbH and WebDesign Solutions.",
        "context": "Vertrag"
    }
    
    print("=" * 60)
    print("TESTING NO MARKDOWN FORMATTING")
    print("=" * 60)
    print(f"Request: {data}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            document = result['generated_doc']
            
            print("SUCCESS!")
            print(f"Document Length: {len(document)} chars")
            print(f"Processing Time: {result['processing_stats'].get('processing_time')}s")
            
            # Check for Markdown patterns
            markdown_patterns = ['**', '##', '###', '*', '_', '`', '```']
            found_markdown = []
            
            for pattern in markdown_patterns:
                if pattern in document:
                    found_markdown.append(pattern)
            
            print(f"\nMarkdown Check:")
            if found_markdown:
                print(f"❌ Found Markdown patterns: {found_markdown}")
            else:
                print("✅ No Markdown formatting found!")
            
            print(f"\nDocument Preview (first 500 chars):")
            print("-" * 60)
            print(document[:500] + "..." if len(document) > 500 else document)
            print("-" * 60)
            
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_no_markdown()