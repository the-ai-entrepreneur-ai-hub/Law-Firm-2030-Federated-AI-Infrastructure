# 🔒 PDF PII Anonymizer - Access Instructions

## ✅ Server Status
The PDF PII Anonymizer server is **RUNNING** and listening on port 5004.

## 🌐 Access URLs

### Option 1: Localhost (Primary)
```
http://localhost:5004
```

### Option 2: IP Address (Alternative)
```
http://172.18.193.15:5004
```

### Option 3: Standalone HTML (Backup)
Open this file in your browser:
```
C:\Users\Administrator\serveless-apps\Law Firm Vision 2030\law-firm-ai\pii_interface.html
```

## 🔧 Troubleshooting

### If "Connection Refused" Error:

1. **Windows Users:**
   - Double-click: `start_pdf_server.bat`
   - Or open PowerShell/CMD and run:
   ```
   cd "C:\Users\Administrator\serveless-apps\Law Firm Vision 2030\law-firm-ai"
   start_pdf_server.bat
   ```

2. **Linux/WSL Users:**
   ```bash
   cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai"
   ./start_pdf_server.sh
   ```

3. **Manual Start:**
   ```bash
   cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai"
   source pii_env/bin/activate
   python3 pdf_pii_web_app.py
   ```

### Firewall Issues:
- Windows Firewall might block port 5004
- Allow Python through Windows Firewall
- Or try IP address: http://172.18.193.15:5004

### Browser Issues:
- Clear browser cache
- Try incognito/private mode
- Try different browser (Chrome, Firefox, Edge)

## 📋 Features Available

✅ **8-Page PDF Upload Support**
- Drag & drop PDF files
- Real-time OCR processing
- Progress tracking

✅ **PII Detection & Anonymization**
- German legal document processing
- Detects: names, phones, emails, IBANs, addresses, case numbers
- Visual statistics and results

✅ **OCR Methods**
- PyPDF2 for text-based PDFs
- Pattern-based fallback for scanned documents
- German language support

## 🎯 Quick Test

1. Open any of the URLs above
2. Click "📄 Load Example" to test with sample text
3. Or upload your 8-page scanned PDF
4. View real-time PII detection results

---

**Need Help?** The server should be accessible at http://localhost:5004 or http://172.18.193.15:5004