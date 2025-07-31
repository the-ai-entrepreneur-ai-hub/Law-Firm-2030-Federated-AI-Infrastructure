# AnwaltsAI - Complete Application Guide

## Overview

AnwaltsAI is a comprehensive legal AI system designed specifically for German law firms. It provides intelligent document processing, PII (Personally Identifiable Information) detection and anonymization, AI-powered legal analysis, and automated document generation capabilities.

## System Architecture

The system consists of two main components:

### 1. Backend API Server (`enhanced_api_server.py`)
- **Port**: 5001
- **Framework**: Flask with JWT authentication
- **Database**: SQLite for user management and document storage
- **AI Integration**: Together.ai API for legal document analysis
- **Features**:
  - User authentication and authorization
  - Document upload and text extraction
  - PII detection and anonymization
  - AI-powered legal analysis
  - Document generation and templates
  - RLHF (Reinforcement Learning from Human Feedback) capabilities

### 2. Frontend Application (`Client/`)
- **Port**: 8080 (HTTP server)
- **Technology**: Pure HTML/CSS/JavaScript with Tailwind CSS
- **Main Files**:
  - `anwalts-ai-app.html` - Primary application interface
  - `anwalts-ai-dashboard.html` - Administrative dashboard
  - `api-client.js` - API communication layer

## Key Features

### 🔐 Authentication System
- Secure JWT-based authentication
- User registration and login
- Session management
- **Default Credentials**:
  - Email: `admin@anwalts-ai.de`
  - Password: `admin123`

### 📄 Document Processing Pipeline
1. **Upload**: Support for PDF, DOCX, TXT files
2. **Text Extraction**: OCR and document parsing
3. **PII Detection**: Identifies names, addresses, phone numbers, email addresses, ID numbers
4. **Anonymization**: Replaces PII with placeholder tokens
5. **AI Analysis**: Legal document analysis using German legal expertise
6. **Translation**: German to English translation capabilities

### 🤖 AI-Powered Legal Analysis
- **Model**: Together.ai DeepSeek-V3 (configurable)
- **Capabilities**:
  - Document type classification
  - Legal risk assessment
  - Contract analysis
  - Compliance checking
  - German legal expertise

### 📋 Document Templates
- Pre-built German legal document templates
- **Available Templates**:
  - Mahnung (Payment Reminder)
  - Geheimhaltungsvereinbarung (NDA)
  - Custom template support

### 🔍 PII Protection
- **Detected Entities**:
  - Names (PERSON)
  - Addresses (LOCATION)
  - Phone numbers (PHONE_NUMBER)
  - Email addresses (EMAIL_ADDRESS)
  - ID numbers (ID_NUMBER)
- **Anonymization**: Secure replacement with contextual placeholders
- **GDPR Compliance**: Designed for German data protection requirements

## Installation & Setup

### Quick Start (Automated)
```bash
# Run the installation script
install_and_run.bat
```

### Manual Setup

#### 1. Backend Setup
```bash
cd law-firm-ai
pip install -r requirements.txt

# Set environment variables
set TOGETHER_API_KEY=your_api_key_here

# Start the enhanced API server
python enhanced_api_server.py
```

#### 2. Frontend Setup
```bash
cd Client
python -m http.server 8080
```

#### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
TOGETHER_API_KEY=your_together_ai_api_key
DEBUG=true
LLM_MODEL_NAME=deepseek-ai/DeepSeek-V3
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/validate` - Token validation

### Document Processing
- `POST /api/upload` - Upload and extract text from documents
- `POST /api/sanitize` - Sanitize text for PII
- `POST /api/ai/respond` - Generate AI responses
- `POST /api/generate` - Complete document generation pipeline

### Templates
- `GET /api/templates` - Get available document templates

### Admin Functions
- `GET /api/health` - System health check
- `POST /api/feedback` - Submit RLHF feedback

## Usage Examples

### 1. Document Analysis Workflow
1. Navigate to `http://localhost:8080/anwalts-ai-app.html`
2. Login with default credentials
3. Upload a German legal document
4. Select processing options:
   - PII detection and anonymization
   - AI analysis
   - Translation to English
5. Review results in organized tabs:
   - Analysis results
   - Detected PII entities
   - AI-generated insights
   - Original/anonymized text

### 2. API Usage
```javascript
// Login
const response = await fetch('http://localhost:5001/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'admin@anwalts-ai.de',
        password: 'admin123'
    })
});

// Process document
const formData = new FormData();
formData.append('file', documentFile);

const processResponse = await fetch('http://localhost:5001/api/generate', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
});
```

## Security Features

### Data Protection
- PII detection and anonymization
- Secure token-based authentication
- HTTPS support (configurable)
- Database encryption capabilities

### Compliance
- GDPR-compliant data handling
- Audit logging
- Data retention policies
- German legal standards compliance

## Configuration

### System Configuration (`system_prompts.py`)
- Legal document types classification
- AI model selection
- Processing parameters
- German legal expertise prompts

### Together.ai Configuration
```python
TOGETHER_AI_CONFIG = {
    "model": "deepseek-ai/DeepSeek-V3",
    "max_tokens": 4000,
    "temperature": 0.1,
    "timeout": 30
}
```

## Monitoring & Logging

### Available Logs
- API access logs
- Processing performance metrics
- Error tracking
- User activity logging

### Health Monitoring
- System health endpoint: `GET /api/health`
- Database connectivity checks
- AI service availability
- Performance metrics

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 5001 and 8080 are available
2. **API key missing**: Set TOGETHER_API_KEY environment variable
3. **Authentication errors**: Check default credentials or create new user
4. **CORS issues**: Ensure both servers are running on correct ports

### Debug Mode
Enable debug mode by setting `DEBUG=true` in environment variables for detailed error logging.

## Development

### Project Structure
```
Law Firm Vision 2030/
├── Client/                     # Frontend application
│   ├── anwalts-ai-app.html    # Main application
│   ├── api-client.js          # API communication
│   └── anwalts-ai-dashboard.html
├── law-firm-ai/               # Backend services
│   ├── enhanced_api_server.py # Main API server
│   ├── system_prompts.py      # AI prompts and config
│   └── requirements.txt       # Python dependencies
├── install_and_run.bat        # Setup script
└── README.md                  # Project documentation
```

### Contributing
1. Follow German legal compliance requirements
2. Maintain PII protection standards
3. Document all API changes
4. Test with sample German legal documents
5. Ensure GDPR compliance in all features

## Support

For technical support or feature requests, please refer to the project repository or contact the development team.

---

**Built for German Law Firms - Secure, Compliant, Intelligent**