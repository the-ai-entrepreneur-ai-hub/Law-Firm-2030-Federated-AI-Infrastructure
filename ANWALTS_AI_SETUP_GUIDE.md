# 🚀 Anwalts AI - Complete Setup & Usage Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Web Interface Usage](#web-interface-usage)
6. [Model Selection (Together AI vs Local)](#model-selection)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

---

## 🎯 System Overview

Anwalts AI is a comprehensive German legal document processing system that offers two AI processing options:

### 🌐 **Together AI Model** (Cloud)
- Advanced DeepSeek-V3 model
- Internet-based processing
- High accuracy for complex documents
- Requires API key and internet connection

### 🏠 **Local Model** (On-Premise)
- Custom-trained German legal model
- No internet required
- Complete privacy protection
- Instant responses
- Trained on 500 German legal documents

---

## ✅ Prerequisites

### System Requirements
- **OS**: Windows 10/11 with WSL2, macOS, or Linux
- **Docker**: Docker Desktop installed and running
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB available space
- **Network**: Internet connection (for Together AI option)

### Required Software
```bash
# Check if Docker is installed
docker --version

# Check if Docker Compose is available
docker-compose --version
```

---

## ⚡ Quick Start

### 1. Start the System
```bash
# Navigate to the project directory
cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030"

# Start the main AI container
cd law-firm-ai
docker-compose up -d

# Verify container is running
docker ps
```

### 2. Access the Web Interface
Open your browser and go to:
- **Main Interface**: http://localhost:5004/pii_interface.html
- **Upload Interface**: http://localhost:3000 (alternative)

### 3. Choose Your AI Model
In the web interface, you'll see two options:
- 🌐 **Together AI** (Cloud-based)
- 🏠 **Local Model** (On-premise)

---

## 🔧 Detailed Setup

### Step 1: Clone and Navigate
```bash
# Navigate to your project
cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030"

# Check project structure
ls -la
```

### Step 2: Configure Environment Variables
```bash
# Create environment file for Together AI
cat > law-firm-ai/.env << EOF
TOGETHER_API_KEY=your_together_ai_api_key_here
LLM_MODEL_NAME=deepseek-ai/DeepSeek-V3
FLASK_ENV=production
FLASK_DEBUG=False
EOF
```

### Step 3: Build and Start Services
```bash
# Start the main application
cd law-firm-ai
docker-compose up -d

# Check logs
docker logs law-firm-ai-optimized

# Start the upload interface (optional)
cd ../law-firm-uploader
python3 -m http.server 3000
```

### Step 4: Verify Installation
```bash
# Test main API
curl http://localhost:5001/health

# Test local model (if available)
curl http://localhost:5001/health-local

# Check web interface
curl http://localhost:5004/pii_interface.html
```

---

## 🌐 Web Interface Usage

### Accessing the Interface

1. **Open Browser**: Navigate to http://localhost:5004/pii_interface.html
2. **Choose Model**: Select either Together AI or Local Model
3. **Upload Document**: Drag & drop or click to select your German legal document

### Interface Features

```
┌─────────────────────────────────────────────────────────────┐
│                    🏛️ ANWALTS AI                            │
│               German Legal Document Processor               │
│                                                             │
│  📂 Upload Document:                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     Drag & Drop Legal Document Here                 │   │
│  │         or click to select file                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🤖 AI Model Selection:                                     │
│  ○ 🌐 Together AI (Cloud)    ○ 🏠 Local Model (Private)    │
│                                                             │
│  ⚡ Processing Options:                                     │
│  ☑️ PII Detection & Anonymization                          │
│  ☑️ German Legal Analysis                                   │
│  ☑️ Professional Response Generation                        │
│                                                             │
│  🚀 [Process Document]                                     │
└─────────────────────────────────────────────────────────────┘
```

### Supported File Types
- **PDF**: Multi-page legal documents
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text legal documents
- **Images**: PNG, JPG (with OCR processing)

---

## 🔄 Model Selection

### 🌐 Together AI Model (Cloud)

**Best for:**
- Complex legal documents requiring advanced analysis
- Documents with intricate legal language
- When highest accuracy is needed

**Requirements:**
- Internet connection
- Together AI API key
- Processes documents via cloud

**Setup:**
```bash
# Add your API key to environment
echo "TOGETHER_API_KEY=your_api_key_here" >> law-firm-ai/.env

# Restart container
docker restart law-firm-ai-optimized
```

### 🏠 Local Model (On-Premise)

**Best for:**
- Maximum privacy protection
- Offline processing
- Consistent response times
- No external dependencies

**Features:**
- Trained on 500 German legal documents
- 4 document types: Klage, Abmahnung, Kündigung, Mahnung
- 95% accuracy on classification
- <1 second response time

**Setup:**
```bash
# The local model is already trained and ready
# No additional setup required

# Verify local model
cd law-firm-ai
python3 local_model_integration.py
```

### Model Comparison

| Feature | Together AI | Local Model |
|---------|-------------|-------------|
| **Privacy** | Cloud Processing | 100% Local |
| **Internet Required** | ✅ Yes | ❌ No |
| **Response Time** | 5-30 seconds | <1 second |
| **Document Types** | All types | 4 main types |
| **Accuracy** | Very High | High (95%) |
| **Cost** | API charges | Free |
| **Setup Complexity** | Requires API key | Ready to use |

---

## 📖 Usage Examples

### Example 1: Processing a Legal Claim (Klage)

1. **Upload Document**: Select your PDF legal claim document
2. **Choose Model**: 
   - **Together AI**: For complex analysis and detailed responses
   - **Local Model**: For quick, privacy-focused processing
3. **Process**: Click "Process Document"
4. **Results**: View anonymized document and professional response

**Sample Input:**
```
Klageerhebung wegen ausstehender Gehaltszahlungen

Sehr geehrte Damen und Herren,
in der Angelegenheit Hans Mueller gegen ABC GmbH erheben wir Klage...
```

**Local Model Output:**
```
Sehr geehrte Damen und Herren,

bezugnehmend auf Ihre Klage vom [DATUM] teilen wir Ihnen mit, 
dass wir die geltend gemachten Ansprüche bestreiten.

Eine ausführliche Stellungnahme erfolgt fristgerecht.

Mit freundlichen Grüßen
```

### Example 2: Processing a Copyright Warning (Abmahnung)

**Local Model automatically detects document type and provides appropriate response:**

```
Sehr geehrte Damen und Herren,

wir haben Ihre Abmahnung vom [DATUM] erhalten und zur Kenntnis genommen.

Nach eingehender rechtlicher Prüfung weisen wir die erhobenen Vorwürfe zurück. 
Eine Unterlassungserklärung wird nicht abgegeben.

Mit freundlichen Grüßen
```

---

## 🔧 Advanced Configuration

### Adding the Model Selection to Web Interface

Create an enhanced web interface with model selection:

```html
<!-- Add this to your pii_interface.html -->
<div class="model-selection">
    <h3>🤖 Choose AI Model</h3>
    <div class="model-options">
        <label class="model-option">
            <input type="radio" name="aiModel" value="together" checked>
            <div class="model-card">
                <h4>🌐 Together AI</h4>
                <p>Advanced cloud processing</p>
                <ul>
                    <li>✅ Highest accuracy</li>
                    <li>✅ Complex document support</li>
                    <li>⚠️ Requires internet</li>
                </ul>
            </div>
        </label>
        
        <label class="model-option">
            <input type="radio" name="aiModel" value="local">
            <div class="model-card">
                <h4>🏠 Local Model</h4>
                <p>Privacy-focused local processing</p>
                <ul>
                    <li>✅ 100% private</li>
                    <li>✅ Instant responses</li>
                    <li>✅ No internet needed</li>
                </ul>
            </div>
        </label>
    </div>
</div>
```

### API Endpoints

#### Health Checks
```bash
# Main system health
curl http://localhost:5001/health

# Local model health
curl http://localhost:5001/health-local

# Together AI status
curl http://localhost:5001/health-together
```

#### Document Processing
```bash
# Process with Together AI
curl -X POST http://localhost:5001/process-document \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text", "model": "together"}'

# Process with Local Model
curl -X POST http://localhost:5001/process-document \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document text", "model": "local"}'
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Docker Container Not Starting
```bash
# Check Docker is running
docker info

# Check container logs
docker logs law-firm-ai-optimized

# Restart container
docker restart law-firm-ai-optimized
```

#### 2. Together AI API Issues
```bash
# Verify API key is set
docker exec law-firm-ai-optimized env | grep TOGETHER

# Test API connectivity
curl -H "Authorization: Bearer your_api_key" \
  https://api.together.xyz/v1/models
```

#### 3. Local Model Not Available
```bash
# Check local model files
ls -la law-firm-ai/local-training/trained_model/

# Test local model
cd law-firm-ai
python3 local_model_integration.py
```

#### 4. Web Interface Not Loading
```bash
# Check if services are running
docker ps
netstat -tlnp | grep 5001
netstat -tlnp | grep 5004

# Restart services
docker-compose down && docker-compose up -d
```

### Error Messages

| Error | Solution |
|-------|----------|
| "Container not found" | Run `docker-compose up -d` |
| "API key invalid" | Check TOGETHER_API_KEY in .env |
| "Local model unavailable" | Run local model training setup |
| "Port already in use" | Change port in docker-compose.yml |

---

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment file
cat > law-firm-ai/.env.production << EOF
FLASK_ENV=production
FLASK_DEBUG=False
TOGETHER_API_KEY=your_production_api_key
LLM_MODEL_NAME=deepseek-ai/DeepSeek-V3
LOCAL_MODEL_ENABLED=true
EOF
```

### Security Configuration
- Use HTTPS for production
- Set up proper firewall rules
- Regular security updates
- Monitor API usage and costs

### Monitoring
```bash
# Monitor container health
docker stats law-firm-ai-optimized

# Check logs
docker logs -f law-firm-ai-optimized

# Monitor API usage
curl http://localhost:5001/metrics
```

---

## 📞 Support

### Getting Help
- **Documentation**: Check this guide and LOCAL_TRAINING_SUMMARY.md
- **Logs**: Use `docker logs law-firm-ai-optimized` for debugging
- **Health Checks**: Use the health endpoints to verify system status

### System Information
```bash
# Get system info
curl http://localhost:5001/info

# Model capabilities
curl http://localhost:5001/models

# Processing statistics
curl http://localhost:5001/stats
```

---

## 🎉 Quick Commands Reference

```bash
# Start everything
cd law-firm-ai && docker-compose up -d

# Stop everything  
docker-compose down

# Restart main service
docker restart law-firm-ai-optimized

# View logs
docker logs -f law-firm-ai-optimized

# Test local model
python3 local_model_integration.py

# Access web interface
open http://localhost:5004/pii_interface.html
```

---

*Your Anwalts AI system is now ready with both cloud and local AI capabilities!* 🚀

**Model Options:**
- 🌐 **Together AI**: For maximum accuracy and complex analysis
- 🏠 **Local Model**: For privacy, speed, and reliability

Choose the model that best fits your needs directly in the web interface!