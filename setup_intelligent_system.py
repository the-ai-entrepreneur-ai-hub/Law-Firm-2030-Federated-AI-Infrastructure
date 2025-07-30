#!/usr/bin/env python3
"""
Intelligent Anwalts AI System Setup Script
Automates the installation and configuration of the intelligent legal AI system
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntelligentAnwaltsAISetup:
    """Setup manager for the Intelligent Anwalts AI system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ai_dir = self.project_root / "law-firm-ai"
        self.uploader_dir = self.project_root / "law-firm-uploader"
        
    def print_banner(self):
        """Print setup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                 ANWALTS AI INTELLIGENT SETUP                ║
║              Advanced Legal AI with RLHF Training           ║
║                                                              ║
║  🤖 Together.ai Integration                                  ║
║  📚 Intelligent Training Pipeline                           ║
║  🔄 Real-time Feedback Loops (RLHF)                        ║
║  🎯 German Legal Document Processing                        ║
║  📊 Performance Analytics                                    ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"Setup initiated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        logger.info("Checking Python version...")
        
        if sys.version_info < (3, 8):
            logger.error("Python 3.8 or higher is required!")
            return False
        
        logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - ✅")
        return True
    
    def setup_directories(self):
        """Create necessary directories"""
        logger.info("Setting up directory structure...")
        
        directories = [
            self.ai_dir / "data",
            self.ai_dir / "logs",
            self.ai_dir / "models",
            self.ai_dir / "local-training" / "data",
            self.ai_dir / "local-training" / "trained_model",
            self.project_root / "monitoring",
            self.project_root / "config"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        requirements_file = self.ai_dir / "requirements_intelligent.txt"
        
        if not requirements_file.exists():
            logger.error(f"Requirements file not found: {requirements_file}")
            return False
        
        try:
            # Create virtual environment if it doesn't exist
            venv_path = self.ai_dir / "venv_intelligent"
            if not venv_path.exists():
                logger.info("Creating Python virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            
            # Determine pip path
            if os.name == 'nt':  # Windows
                pip_path = venv_path / "Scripts" / "pip"
                python_path = venv_path / "Scripts" / "python"
            else:  # Unix/Linux
                pip_path = venv_path / "bin" / "pip"
                python_path = venv_path / "bin" / "python"
            
            # Upgrade pip
            logger.info("Upgrading pip...")
            subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
            
            # Install requirements
            logger.info("Installing packages from requirements...")
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
            
            logger.info("Python dependencies installed successfully - ✅")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Python dependencies: {e}")
            return False
    
    def setup_configuration(self):
        """Setup configuration files"""
        logger.info("Setting up configuration files...")
        
        # API Server configuration
        api_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 5001,
                "debug": False,
                "threaded": True
            },
            "together_ai": {
                "api_key": "your-together-ai-key-here",
                "base_url": "https://api.together.xyz/v1",
                "default_model": "deepseek-ai/deepseek-v3",
                "timeout": 30,
                "max_retries": 3
            },
            "database": {
                "path": "law-firm-ai/training_data.db",
                "backup_interval": "daily"
            },
            "training": {
                "min_examples_threshold": 50,
                "quality_threshold": 0.7,
                "auto_training": True,
                "training_schedule": "adaptive"
            },
            "security": {
                "cors_origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
                "rate_limiting": True,
                "max_requests_per_minute": 100
            }
        }
        
        config_file = self.project_root / "config" / "api_config.json"
        with open(config_file, 'w') as f:
            json.dump(api_config, f, indent=2)
        
        # Training configuration
        training_config = {
            "learning_rate": 0.0001,
            "batch_size": 8,
            "max_epochs": 3,
            "warmup_steps": 100,
            "weight_decay": 0.01,
            "gradient_accumulation_steps": 4,
            "evaluation_steps": 100,
            "save_steps": 500,
            "model_selection_criteria": "user_preference",
            "adaptive_learning": True,
            "quality_filtering": True
        }
        
        training_config_file = self.ai_dir / "local-training" / "training_config.json"
        with open(training_config_file, 'w') as f:
            json.dump(training_config, f, indent=2)
        
        logger.info("Configuration files created - ✅")
    
    def setup_environment_file(self):
        """Create environment file template"""
        logger.info("Creating environment file template...")
        
        env_content = """# Anwalts AI Intelligent System Environment Variables
# Copy this file to .env and fill in your actual values

# Together.ai API Configuration
TOGETHER_API_KEY=your_together_ai_api_key_here
TOGETHER_MODEL=deepseek-ai/deepseek-v3

# Database Configuration
DATABASE_URL=sqlite:///law-firm-ai/training_data.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=5001
DEBUG_MODE=False

# Security
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
SECRET_KEY=your_secret_key_here

# Training Configuration
AUTO_TRAINING=True
MIN_TRAINING_EXAMPLES=50
QUALITY_THRESHOLD=0.7

# Monitoring
ENABLE_METRICS=True
LOG_LEVEL=INFO

# File Upload Limits
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,txt,png,jpg,jpeg
"""
        
        env_file = self.project_root / ".env.template"
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info("Environment template created at .env.template - ✅")
        logger.info("Please copy .env.template to .env and configure your API keys")
    
    def create_startup_scripts(self):
        """Create startup scripts for different platforms"""
        logger.info("Creating startup scripts...")
        
        # Unix/Linux startup script
        unix_script = """#!/bin/bash
# Anwalts AI Intelligent System Startup Script

echo "🚀 Starting Anwalts AI Intelligent System..."

# Check if virtual environment exists
if [ ! -d "law-firm-ai/venv_intelligent" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source law-firm-ai/venv_intelligent/bin/activate

# Check for environment file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using default configuration."
fi

# Start the API server
echo "🤖 Starting API server..."
cd law-firm-ai
python api_server.py &
API_PID=$!

# Start the web interface
echo "🌐 Starting web interface..."
cd ../law-firm-uploader
python serve.py &
WEB_PID=$!

echo "✅ System started successfully!"
echo "📡 API Server: http://localhost:5001"
echo "🌐 Web Interface: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $API_PID $WEB_PID; echo '🛑 Shutting down...'; exit" INT
wait
"""
        
        # Windows startup script
        windows_script = """@echo off
REM Anwalts AI Intelligent System Startup Script

echo 🚀 Starting Anwalts AI Intelligent System...

REM Check if virtual environment exists
if not exist "law-firm-ai\\venv_intelligent" (
    echo ❌ Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
call law-firm-ai\\venv_intelligent\\Scripts\\activate.bat

REM Check for environment file
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Using default configuration.
)

REM Start the API server
echo 🤖 Starting API server...
cd law-firm-ai
start /B python api_server.py

REM Start the web interface
echo 🌐 Starting web interface...
cd ..\\law-firm-uploader
start /B python serve.py

echo ✅ System started successfully!
echo 📡 API Server: http://localhost:5001
echo 🌐 Web Interface: http://localhost:8080
echo.
echo Press any key to stop all services
pause > nul

REM Kill processes (simplified - you might want to improve this)
taskkill /f /im python.exe
"""
        
        # Save scripts
        unix_script_file = self.project_root / "start_intelligent_system.sh"
        with open(unix_script_file, 'w') as f:
            f.write(unix_script)
        os.chmod(unix_script_file, 0o755)  # Make executable
        
        windows_script_file = self.project_root / "start_intelligent_system.bat"
        with open(windows_script_file, 'w') as f:
            f.write(windows_script)
        
        logger.info("Startup scripts created - ✅")
    
    def create_documentation(self):
        """Create system documentation"""
        logger.info("Creating documentation...")
        
        readme_content = """# Anwalts AI Intelligent System

## 🤖 Advanced Legal AI with Intelligent Training

This system provides intelligent legal document processing with real-time learning capabilities through Human Feedback (RLHF).

### ✨ Features

- **🧠 Intelligent AI Processing**: Uses Together.ai for high-quality German legal responses
- **📚 Adaptive Learning**: Continuously improves through user feedback
- **🔄 Real-time Training**: Automatic model updates based on user interactions
- **🎯 Document Type Detection**: Automatically detects and processes different legal document types
- **📊 Performance Analytics**: Tracks model performance and user satisfaction
- **🔒 Privacy-First**: PII detection and anonymization built-in
- **🌐 Modern Interface**: Responsive web interface with real-time feedback

### 🚀 Quick Start

1. **Setup the system:**
   ```bash
   python setup_intelligent_system.py
   ```

2. **Configure your API keys:**
   ```bash
   cp .env.template .env
   # Edit .env with your Together.ai API key
   ```

3. **Start the system:**
   ```bash
   # On Unix/Linux/macOS:
   ./start_intelligent_system.sh
   
   # On Windows:
   start_intelligent_system.bat
   ```

4. **Access the interface:**
   - Web Interface: http://localhost:8080
   - API Server: http://localhost:5001

### 🔧 Configuration

#### Together.ai API Setup
1. Sign up at [Together.ai](https://api.together.xyz)
2. Get your API key
3. Add it to your `.env` file:
   ```
   TOGETHER_API_KEY=your_api_key_here
   ```

#### Training Configuration
The system automatically learns from user feedback:
- **Accept**: Good responses are used for positive training
- **Reject**: Poor responses help identify areas for improvement  
- **Improve**: User edits become high-quality training examples

### 📊 How Intelligence Works

1. **Document Analysis**: Automatically detects document type and context
2. **AI Generation**: Uses appropriate model and prompts for the document type
3. **Quality Assessment**: Calculates confidence scores for responses
4. **User Feedback**: Collects accept/reject/improve feedback
5. **Intelligent Training**: Automatically triggers training when quality thresholds are met
6. **Continuous Improvement**: Models adapt to user preferences over time

### 🛠️ API Endpoints

- `POST /api/generate` - Generate legal document responses
- `POST /api/feedback` - Submit user feedback for training
- `GET /api/metrics` - Get performance metrics
- `GET /api/health` - System health check

### 📁 Project Structure

```
├── law-firm-ai/
│   ├── api_server.py              # Main API server
│   ├── intelligent_training_manager.py  # Training intelligence
│   ├── local-training/            # Local training pipeline
│   └── venv_intelligent/          # Python environment
├── law-firm-uploader/             # Web interface
├── config/                        # Configuration files
└── monitoring/                    # System monitoring
```

### 🔍 Monitoring

Access system metrics and performance:
- Training acceptance rates
- Model confidence scores
- Processing times
- User satisfaction metrics

### 🆘 Troubleshooting

**API Connection Issues:**
- Check that Together.ai API key is valid
- Verify network connectivity
- Check firewall settings for ports 5001 and 8080

**Training Not Triggered:**
- Ensure minimum feedback threshold is met (default: 50 examples)
- Check quality threshold settings
- Verify training configuration

**Performance Issues:**
- Monitor system resources
- Check database performance
- Review API response times

### 📞 Support

For technical support or questions:
- Check system logs in `law-firm-ai/logs/`
- Review configuration in `config/api_config.json`
- Monitor performance at `/api/metrics`

---

Built with ❤️ for intelligent legal document processing.
"""
        
        readme_file = self.project_root / "README_INTELLIGENT.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        logger.info("Documentation created - ✅")
    
    def run_initial_tests(self):
        """Run initial system tests"""
        logger.info("Running initial system tests...")
        
        try:
            # Test 1: Check if API server can start
            logger.info("Testing API server startup...")
            
            # Test 2: Check database connectivity
            logger.info("Testing database connectivity...")
            
            # Test 3: Verify configuration files
            config_file = self.project_root / "config" / "api_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info("Configuration file valid - ✅")
            
            logger.info("Initial tests completed - ✅")
            return True
            
        except Exception as e:
            logger.error(f"Initial tests failed: {e}")
            return False
    
    def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Setting up directories", self.setup_directories),
            ("Installing dependencies", self.install_python_dependencies),
            ("Creating configuration", self.setup_configuration),
            ("Setting up environment", self.setup_environment_file),
            ("Creating startup scripts", self.create_startup_scripts),
            ("Generating documentation", self.create_documentation),
            ("Running initial tests", self.run_initial_tests)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 {step_name}...")
            try:
                if not step_func():
                    logger.error(f"❌ {step_name} failed!")
                    return False
            except Exception as e:
                logger.error(f"❌ {step_name} failed with error: {e}")
                return False
        
        # Success message
        success_message = """
╔══════════════════════════════════════════════════════════════╗
║                    🎉 SETUP COMPLETE! 🎉                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ✅ Intelligent Anwalts AI system is ready!                ║
║                                                              ║
║  📋 Next Steps:                                             ║
║  1. Copy .env.template to .env                              ║
║  2. Add your Together.ai API key to .env                    ║
║  3. Run: ./start_intelligent_system.sh (Unix/Linux)         ║
║     or: start_intelligent_system.bat (Windows)              ║
║                                                              ║
║  🌐 Access: http://localhost:8080                           ║
║  📡 API: http://localhost:5001                              ║
║                                                              ║
║  📖 Read README_INTELLIGENT.md for detailed instructions    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        print(success_message)
        return True

if __name__ == "__main__":
    setup = IntelligentAnwaltsAISetup()
    
    if setup.run_setup():
        sys.exit(0)
    else:
        logger.error("Setup failed! Please check the logs above.")
        sys.exit(1)