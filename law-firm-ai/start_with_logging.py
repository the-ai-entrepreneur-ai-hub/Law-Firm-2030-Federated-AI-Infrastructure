#!/usr/bin/env python3
"""
Start FastAPI server with enhanced real-time logging
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Enhanced logging configuration
def setup_logging():
    """Setup enhanced logging with real-time output"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    
    # File handler for persistent logs
    log_file = log_dir / f"anwalts_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    # Configure FastAPI app logger
    app_logger = logging.getLogger("simple_fastapi_backend")
    app_logger.setLevel(logging.INFO)
    
    return log_file

def main():
    print("=" * 60)
    print("🚀 AnwaltsAI FastAPI Server with Enhanced Logging")
    print("=" * 60)
    
    # Setup logging
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    
    # Environment check
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        logger.info(f"Together.ai API key configured: {masked_key}")
    else:
        logger.warning("TOGETHER_API_KEY not found - running in mock mode")
    
    logger.info(f"Log file: {log_file}")
    logger.info("Server starting with real-time logging...")
    
    print(f"\n📋 Server Information:")
    print(f"   • URL: http://localhost:8000")
    print(f"   • Docs: http://localhost:8000/docs")
    print(f"   • Log file: {log_file}")
    print(f"   • CORS: Enabled for React frontend")
    
    print(f"\n🔍 Real-time API Monitoring:")
    print(f"   • All requests and responses will be logged")
    print(f"   • PII sanitization events tracked")
    print(f"   • AI response generation monitored")
    print(f"   • Error handling with detailed stack traces")
    
    print(f"\n💡 Usage:")
    print(f"   • Watch this console for real-time logs")
    print(f"   • Press Ctrl+C to stop the server")
    print(f"   • Logs are also saved to: {log_file}")
    
    print("=" * 60)
    print("🟢 Server Ready - Watching for requests...")
    print("=" * 60)
    
    try:
        # Start the server with enhanced logging
        uvicorn.run(
            "simple_fastapi_backend:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            use_colors=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n👋 Server stopped. Logs saved to:", log_file)
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()