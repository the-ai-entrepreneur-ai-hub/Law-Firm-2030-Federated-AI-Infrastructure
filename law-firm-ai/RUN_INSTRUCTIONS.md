# Law Firm AI with Translation - Docker Setup

## Prerequisites
- Docker and Docker Compose installed
- Set your TOGETHER_API_KEY in the docker-compose.yml file

## Quick Start

1. **Build and run with Docker Compose:**
```bash
cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai"
docker-compose up --build sanitizer
```

2. **The application will be available at:**
   - Main API: http://localhost:5001
   - Health check: http://localhost:5001/health

## API Usage

### Process a Document with Translation
Send a POST request to `/process-document` with a German document file:

```bash
curl -X POST \
  -F "file=@your_german_document.pdf" \
  http://localhost:5001/process-document
```

### Response Format
The API now returns results in English with:
- `final_response.original_text_preview`: First 200 characters of the original German text
- `final_response.anonymized_text_english`: The anonymized text translated to English
- `final_response.detected_pii_entities`: List of detected PII entities with confidence scores
- `final_response.llm_analysis_english`: AI analysis translated to English

## Features Added
✅ **Translation Support**: German to English translation using Google Translate
✅ **Real-time Results**: See PII removal, anonymization, and AI analysis in English
✅ **Backup Created**: Original secure_sanitizer.py backed up as secure_sanitizer_backup.py
✅ **Docker Support**: Containerized application with all dependencies

## What You'll See
1. **Detected PII Entities**: List of personally identifiable information found (names, IDs, phone numbers, etc.)
2. **Anonymized Text (English)**: The German text with PII replaced by placeholders, translated to English
3. **AI Analysis (English)**: AI model's analysis of the document, translated to English

## Environment Variables
Update in docker-compose.yml:
- `TOGETHER_API_KEY`: Your Together AI API key
- `LLM_MODEL_NAME`: AI model to use (default: deepseek-ai/DeepSeek-V3)
- `DEBUG`: Set to true for debug mode

## Logs
View logs in real-time:
```bash
docker-compose logs -f sanitizer
```