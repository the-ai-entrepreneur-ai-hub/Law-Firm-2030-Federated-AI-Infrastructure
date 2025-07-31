# 🏛️ AnwaltsAI - Professional Legal AI Platform

**German Legal Document Generation with AI-Powered Assistance**

---

## 🚀 **Quick Start**

### **Option 1: Automated Startup (Recommended)**
```bash
# Windows
start_anwalts_ai.bat

# Cross-platform
python start_anwalts_ai.py
```

### **Option 2: Manual Startup**
```bash
# Terminal 1: Backend API
cd law-firm-ai
python enhanced_api_server.py

# Terminal 2: Frontend Web Server
cd Client
python -m http.server 8080
```

### **Access Application**
- **URL**: http://localhost:8080/anwalts-ai-app.html
- **Login**: admin@anwalts-ai.de / admin123

---

## 📋 **Features**

✅ **Authentication System**: Secure login with JWT tokens  
✅ **Dashboard**: Real-time statistics and activity feed  
✅ **Document Generator**: AI-powered legal document creation  
✅ **Email Management**: Mock email system with AI responses  
✅ **Template System**: Legal document templates (CRUD)  
✅ **Responsive Design**: Works on desktop, tablet, mobile  

---

## 🏗️ **Architecture**

### **Frontend** (`Client/`)
- `anwalts-ai-app.html` - Main application
- `api-client.js` - API integration layer
- Glass morphism design with 3D animations

### **Backend** (`law-firm-ai/`)
- `enhanced_api_server.py` - Flask API server
- SQLite database with user management
- Together.ai integration for German legal LLM

---

## 📞 **Support**

- **Health Check**: http://localhost:5001/health
- **Documentation**: `ANWALTS_AI_COMPLETE_DEPLOYMENT.md`
- **Architecture**: `RECONSTRUCTION_PLAN.md`

---

**Status: ✅ COMPLETE & READY FOR USE**