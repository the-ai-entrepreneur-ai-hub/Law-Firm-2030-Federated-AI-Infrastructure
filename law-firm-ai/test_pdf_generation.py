#!/usr/bin/env python3
"""
Test PDF generation functionality
"""

import requests
import json

def test_pdf_generation():
    base_url = "http://localhost:8003"
    
    print("=" * 60)
    print("TESTING PDF GENERATION")
    print("=" * 60)
    
    # Step 1: Generate a document
    print("1. Generating document...")
    
    generate_data = {
        "text": "Create a professional German rental agreement (Mietvertrag) for an apartment in Munich between landlord Mueller and tenant Schmidt.",
        "context": "Mietvertrag"
    }
    
    try:
        response = requests.post(f"{base_url}/api/generate", json=generate_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Document generated successfully!")
            print(f"   Length: {len(result['generated_doc'])} characters")
            print(f"   Processing time: {result['processing_stats']['processing_time']}s")
            
            # Check if PDF is available
            stats = result['processing_stats']
            if stats.get('pdf_available'):
                document_id = stats.get('document_id')
                print(f"   PDF Available: Yes")
                print(f"   Document ID: {document_id}")
                
                # Step 2: Download PDF
                print("\n2. Downloading PDF...")
                
                pdf_response = requests.get(f"{base_url}/api/download-pdf/{document_id}")
                
                if pdf_response.status_code == 200:
                    # Save PDF to file
                    filename = f"test_document_{document_id[:8]}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(pdf_response.content)
                    
                    print(f"✅ PDF downloaded successfully!")
                    print(f"   Filename: {filename}")
                    print(f"   Size: {len(pdf_response.content)} bytes")
                    
                    # Check content type
                    content_type = pdf_response.headers.get('content-type')
                    print(f"   Content Type: {content_type}")
                    
                else:
                    print(f"❌ PDF download failed: {pdf_response.status_code}")
                    print(f"   Error: {pdf_response.text}")
                    
            else:
                print("❌ PDF generation not available")
                
        else:
            print(f"❌ Document generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("PDF GENERATION TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_pdf_generation()