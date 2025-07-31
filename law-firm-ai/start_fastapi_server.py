#!/usr/bin/env python3
"""
AnwaltsAI FastAPI Server Startup Script
Comprehensive startup with environment checks and logging
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def check_environment():
    """Check required environment variables and dependencies"""
    print("Checking environment...")
    
    # Check Together.ai API key
    together_key = os.environ.get("TOGETHER_API_KEY")
    if not together_key:
        print("ERROR: TOGETHER_API_KEY environment variable not set!")
        print("   Please set your Together.ai API key:")
        print("   export TOGETHER_API_KEY='your_api_key_here'")
        return False
    else:
        masked_key = together_key[:8] + "..." + together_key[-4:] if len(together_key) > 12 else "***"
        print(f"OK: Together.ai API key configured: {masked_key}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"ERROR: Python 3.8+ required, got {sys.version}")
        return False
    else:
        print(f"OK: Python version: {sys.version.split()[0]}")
    
    # Check critical files exist
    required_files = [
        "fastapi_backend.py",
        "secure_sanitizer.py", 
        "system_prompts.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"ERROR: Required file missing: {file}")
            return False
        else:
            print(f"OK: Found: {file}")
    
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "spacy", "together", 
        "pdfplumber", "pytesseract", "PIL", "cv2"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "PIL":
                import PIL
            elif package == "cv2":
                import cv2
            else:
                __import__(package)
            print(f"OK: {package}")
        except ImportError:
            print(f"MISSING: {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements_fastapi.txt")
        return False
    
    return True

def check_spacy_model():
    """Check if German spaCy model is installed"""
    print("\nChecking spaCy German model...")
    
    try:
        import spacy
        # Try to load German model
        try:
            nlp = spacy.load("de_core_news_lg")
            print("OK: de_core_news_lg (large) model loaded")
            return True
        except OSError:
            try:
                nlp = spacy.load("de_core_news_md")
                print("OK: de_core_news_md (medium) model loaded")
                return True
            except OSError:
                try:
                    nlp = spacy.load("de_core_news_sm")
                    print("WARNING: de_core_news_sm (small) model loaded - reduced accuracy")
                    return True
                except OSError:
                    print("ERROR: No German spaCy model found!")
                    print("   Install with: python -m spacy download de_core_news_lg")
                    return False
    except ImportError:
        print("ERROR: spaCy not installed")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\nStarting AnwaltsAI FastAPI Backend Server...")
    print("=" * 60)
    
    try:
        import uvicorn
        from fastapi_backend import app
        
        print("Server will be available at:")
        print("   - Local:   http://localhost:8000")
        print("   - Network: http://0.0.0.0:8000")
        print("\nAPI Documentation:")
        print("   - Interactive: http://localhost:8000/docs")
        print("   - OpenAPI:     http://localhost:8000/redoc")
        print("\nAvailable Endpoints:")
        print("   - POST /api/upload     - Upload documents (PDF, DOCX, images)")
        print("   - POST /api/sanitize   - PII sanitization")
        print("   - POST /api/ai/respond - AI response generation")
        print("   - POST /api/generate   - Complete document generation")
        print("   - GET  /api/templates  - Document templates")
        print("   - GET  /health         - Health check")
        print("\n" + "=" * 60)
        print("Security Features Active:")
        print("   - Zero-trust PII sanitization")
        print("   - German legal document expertise")
        print("   - Multi-format document processing")
        print("   - CORS enabled for React frontend")
        print("\nReady for React frontend integration!")
        print("=" * 60)
        
        # Start the server
        uvicorn.run(
            "fastapi_backend:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nERROR: Server startup failed: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("AnwaltsAI Backend Server Startup")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed!")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\nDependency check failed!")
        sys.exit(1)
    
    # Check spaCy model
    if not check_spacy_model():
        print("\nspaCy model check failed - continuing with reduced functionality")
    
    print("\nAll checks passed!")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()