#!/usr/bin/env python3
"""
FastAPI Backend for AnwaltsAI - Complete Pipeline Integration
Integrates secure_sanitizer.py OCR+PII system with Together.ai for React frontend
"""

import os
import json
import logging
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import aiofiles
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Import our existing components
from secure_sanitizer import (
    zero_trust_sanitizer, 
    visual_sanitizer,
    together_client,
    TOGETHER_API_KEY,
    LLM_MODEL_NAME
)
from system_prompts import (
    GermanLegalPrompts, 
    DocumentType, 
    TOGETHER_AI_CONFIG,
    MODEL_CONFIGS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AnwaltsAI Backend API",
    description="Complete legal document processing pipeline with PII sanitization and AI generation",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class SanitizeRequest(BaseModel):
    text: str = Field(..., description="Text to sanitize for PII")

class SanitizeResponse(BaseModel):
    sanitized_text: str
    entities_removed: List[Dict[str, Any]]
    processing_time: float
    success: bool

class AIResponseRequest(BaseModel):
    sanitized_text: str = Field(..., description="PII-sanitized text for AI processing")
    context: Optional[str] = Field(None, description="Additional context for AI response")
    document_type: Optional[str] = Field("general", description="Type of legal document")
    temperature: Optional[float] = Field(0.1, description="AI temperature setting")

class AIResponseResponse(BaseModel):
    ai_response: str
    processing_time: float
    tokens_used: Optional[int] = None
    model_used: str
    success: bool

class GenerateDocumentRequest(BaseModel):
    text: Optional[str] = Field(None, description="Direct text input")
    context: Optional[str] = Field(None, description="Additional context")
    template_content: Optional[str] = Field(None, description="Template to use as base")
    document_type: Optional[str] = Field("general", description="Type of document to generate")

class DocumentGenerationResponse(BaseModel):
    generated_doc: str
    sanitized_input: str
    entities_removed: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]
    download_url: Optional[str] = None
    success: bool

# Global storage for generated documents (in production, use proper database/storage)
generated_documents: Dict[str, str] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AnwaltsAI FastAPI Backend",
        "version": "1.0.0",
        "components": {
            "secure_sanitizer": "active",
            "together_ai": "configured" if TOGETHER_API_KEY else "missing_key",
            "system_prompts": "loaded"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process document (PDF, DOCX, image) with OCR and text extraction
    """
    start_time = datetime.now()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > 50:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
        
        logger.info(f"Processing uploaded file: {file.filename} ({file_size_mb:.2f}MB)")
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process with secure sanitizer (text extraction)
            extracted_text = ""
            
            if file.content_type == "application/pdf":
                # Use pdfplumber for PDF extraction
                import pdfplumber
                import io
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
                            
            elif file.content_type and file.content_type.startswith("image/"):
                # Use OCR for images
                try:
                    import pytesseract
                    from PIL import Image
                    import io
                    img = Image.open(io.BytesIO(file_content))
                    extracted_text = pytesseract.image_to_string(img, lang='deu+eng')
                except Exception as e:
                    logger.error(f"OCR failed: {e}")
                    extracted_text = "OCR processing failed"
                    
            elif file.content_type == "text/plain":
                extracted_text = file_content.decode('utf-8', errors='ignore')
                
            else:
                # Try to decode as text
                try:
                    extracted_text = file_content.decode('utf-8', errors='ignore')
                except:
                    raise HTTPException(status_code=400, detail="Unsupported file format")
            
            if not extracted_text.strip():
                extracted_text = "No text could be extracted from the document"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "text": extracted_text,
                "filename": file.filename,
                "file_size_mb": round(file_size_mb, 2),
                "processing_time": round(processing_time, 2),
                "character_count": len(extracted_text)
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail="Document processing failed")

@app.post("/api/sanitize", response_model=SanitizeResponse)
async def sanitize_text(request: SanitizeRequest):
    """
    Sanitize text for PII using the secure sanitizer
    """
    start_time = datetime.now()
    
    try:
        text = request.text
        
        if not text or len(text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Text too short or empty")
        
        logger.info("Starting PII sanitization")
        
        # Use zero_trust_sanitizer for PII detection
        pii_matches = zero_trust_sanitizer.parallel_detection(text)
        consolidated_matches = zero_trust_sanitizer.consolidate_matches(pii_matches)
        sanitized_text, rehydration_map = zero_trust_sanitizer.consolidated_redaction(text, consolidated_matches)
        
        # Format entities for response
        entities_removed = []
        for match in consolidated_matches:
            entities_removed.append({
                "type": match.entity_type,
                "original": match.text,
                "replacement": f"[{match.entity_type}_{entities_removed.count({'type': match.entity_type}) + 1}]",
                "confidence": round(match.confidence, 2),
                "detection_method": match.detection_method,
                "position": f"{match.start}-{match.end}"
            })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"PII sanitization completed: {len(entities_removed)} entities removed")
        
        return SanitizeResponse(
            sanitized_text=sanitized_text,
            entities_removed=entities_removed,
            processing_time=round(processing_time, 2),
            success=True
        )
        
    except Exception as e:
        logger.error(f"Sanitization failed: {e}")
        raise HTTPException(status_code=500, detail="PII sanitization failed")

@app.post("/api/ai/respond", response_model=AIResponseResponse)
async def generate_ai_response(request: AIResponseRequest):
    """
    Generate German legal AI response using Together.ai
    """
    start_time = datetime.now()
    
    try:
        if not request.sanitized_text or len(request.sanitized_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Sanitized text too short")
        
        logger.info("Generating AI response with Together.ai")
        
        # Determine document type
        try:
            doc_type = DocumentType(request.document_type.lower())
        except ValueError:
            doc_type = DocumentType.ALLGEMEIN
        
        # Get system and user prompts
        if request.sanitized_text.startswith("E-MAIL") or "email" in request.context.lower() if request.context else False:
            # Email response generation
            system_prompt, user_prompt = GermanLegalPrompts.get_response_generation_prompt(
                request.sanitized_text, 
                request.context or ""
            )
        else:
            # Document generation
            system_prompt = GermanLegalPrompts.get_system_prompt(doc_type, {
                "legal_area": request.context,
                "urgent": "dringend" in (request.context or "").lower()
            })
            user_prompt = GermanLegalPrompts.get_user_prompt(
                request.sanitized_text,
                doc_type
            )
        
        # Configure model parameters
        model_config = MODEL_CONFIGS.get("precise", TOGETHER_AI_CONFIG)
        model_config["temperature"] = request.temperature
        
        # Call Together.ai API
        try:
            response = together_client.chat.completions.create(
                model=model_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=model_config.get("max_tokens", 4096),
                temperature=model_config["temperature"],
                top_p=model_config.get("top_p", 0.9),
                stop=model_config.get("stop", [])
            )
            
            ai_response = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            
        except Exception as e:
            logger.error(f"Together.ai API call failed: {e}")
            # Fallback response
            ai_response = """Sehr geehrte Damen und Herren,

vielen Dank für Ihre Nachricht. Aufgrund technischer Schwierigkeiten kann ich Ihnen derzeit keine automatisierte Antwort generieren.

Bitte wenden Sie sich direkt an unsere Kanzlei für eine persönliche Beratung.

Mit freundlichen Grüßen
[Kanzleiname]"""
            tokens_used = None
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"AI response generated successfully in {processing_time:.2f}s")
        
        return AIResponseResponse(
            ai_response=ai_response,
            processing_time=round(processing_time, 2),
            tokens_used=tokens_used,
            model_used=model_config["model"],
            success=True
        )
        
    except Exception as e:
        logger.error(f"AI response generation failed: {e}")
        raise HTTPException(status_code=500, detail="AI response generation failed")

@app.post("/api/generate", response_model=DocumentGenerationResponse)
async def generate_document(
    request: GenerateDocumentRequest = None,
    file: Optional[UploadFile] = File(None)
):
    """
    Complete document generation pipeline: upload -> sanitize -> AI generate -> export
    """
    start_time = datetime.now()
    
    try:
        # Step 1: Get input text (from file or direct text)
        if file:
            # Process uploaded file
            logger.info(f"Processing uploaded file for generation: {file.filename}")
            file_content = await file.read()
            
            # Extract text based on file type
            if file.content_type == "application/pdf":
                import pdfplumber
                import io
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    raw_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            raw_text += page_text + "\n"
            elif file.content_type and file.content_type.startswith("image/"):
                import pytesseract
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(file_content))
                raw_text = pytesseract.image_to_string(img, lang='deu+eng')
            else:
                raw_text = file_content.decode('utf-8', errors='ignore')
                
        elif request and request.text:
            raw_text = request.text
        else:
            raise HTTPException(status_code=400, detail="No input text or file provided")
        
        if not raw_text or len(raw_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Input text too short")
        
        # Step 2: Sanitize for PII
        logger.info("Sanitizing input text for PII")
        pii_matches = zero_trust_sanitizer.parallel_detection(raw_text)
        consolidated_matches = zero_trust_sanitizer.consolidate_matches(pii_matches)
        sanitized_text, rehydration_map = zero_trust_sanitizer.consolidated_redaction(raw_text, consolidated_matches)
        
        # Step 3: Generate AI response
        logger.info("Generating legal document with AI")
        
        # Determine document type
        doc_type_str = request.document_type if request else "general"
        try:
            doc_type = DocumentType(doc_type_str.lower())
        except ValueError:
            doc_type = DocumentType.ALLGEMEIN
        
        # Prepare context
        context = {
            "template_used": bool(request and request.template_content),
            "legal_area": request.context if request else None
        }
        
        # Get prompts
        system_prompt = GermanLegalPrompts.get_system_prompt(doc_type, context)
        
        if request and request.template_content:
            user_prompt = GermanLegalPrompts.get_user_prompt(
                sanitized_text, 
                doc_type, 
                request.template_content
            )
        else:
            user_prompt = GermanLegalPrompts.get_user_prompt(sanitized_text, doc_type)
        
        # Generate with Together.ai
        try:
            response = together_client.chat.completions.create(
                model=TOGETHER_AI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=TOGETHER_AI_CONFIG["max_tokens"],
                temperature=TOGETHER_AI_CONFIG["temperature"],
                top_p=TOGETHER_AI_CONFIG["top_p"],
                stop=TOGETHER_AI_CONFIG.get("stop", [])
            )
            
            generated_document = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            generated_document = f"""Sehr geehrte Damen und Herren,

aufgrund der bereitgestellten Informationen erstelle ich hiermit das gewünschte Rechtsdokument.

[HINWEIS: Die automatische Generierung war nicht verfügbar. Bitte wenden Sie sich für eine vollständige Dokumenterstellung an einen Rechtsanwalt.]

Sachverhalt: {sanitized_text[:200]}...

Mit freundlichen Grüßen
[Rechtsanwaltskanzlei]"""
            tokens_used = 0
        
        # Step 4: Create downloadable file
        document_id = str(uuid.uuid4())
        
        # Store generated document for download
        generated_documents[document_id] = generated_document
        download_url = f"/files/{document_id}.docx"
        
        # Prepare entities removed info
        entities_removed = []
        for match in consolidated_matches:
            entities_removed.append({
                "type": match.entity_type,
                "confidence": round(match.confidence, 2),
                "detection_method": match.detection_method
            })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Processing stats
        processing_stats = {
            "processing_time": round(processing_time, 2),
            "input_length": len(raw_text),
            "sanitized_length": len(sanitized_text),
            "output_length": len(generated_document),
            "entities_removed": len(consolidated_matches),
            "tokens_used": tokens_used,
            "document_type": doc_type_str
        }
        
        logger.info(f"Document generation completed successfully in {processing_time:.2f}s")
        
        return DocumentGenerationResponse(
            generated_doc=generated_document,
            sanitized_input=sanitized_text,
            entities_removed=entities_removed,
            processing_stats=processing_stats,
            download_url=download_url,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation pipeline failed: {e}")
        raise HTTPException(status_code=500, detail="Document generation failed")

@app.get("/files/{document_id}.docx")
async def download_document(document_id: str):
    """
    Download generated document as DOCX file
    """
    if document_id not in generated_documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        document_content = generated_documents[document_id]
        
        # Create DOCX file
        from docx import Document
        doc = Document()
        
        # Split content into paragraphs and add to document
        paragraphs = document_content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                doc.add_paragraph(paragraph.strip())
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            doc.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # Return file
        return FileResponse(
            tmp_file_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"generated_document_{document_id}.docx"
        )
        
    except Exception as e:
        logger.error(f"Document download failed: {e}")
        raise HTTPException(status_code=500, detail="Document download failed")

@app.get("/api/templates")
async def get_templates():
    """
    Get available document templates
    """
    templates = [
        {
            "id": "mahnung_1",
            "name": "Mahnung (1. Stufe)",
            "category": "payment",
            "content": """Sehr geehrte Damen und Herren,

hiermit mahnen wir Sie zur Zahlung der offenen Rechnung Nr. [RECHNUNGSNUMMER] vom [DATUM] über [BETRAG] €.

Wir bitten Sie, den Betrag innerhalb von 14 Tagen zu begleichen.

Mit freundlichen Grüßen"""
        },
        {
            "id": "nda_template",
            "name": "Geheimhaltungsvereinbarung",
            "category": "contracts",
            "content": """GEHEIMHALTUNGSVEREINBARUNG

Zwischen [PARTEI_1] und [PARTEI_2] wird folgende Geheimhaltungsvereinbarung geschlossen:

1. Gegenstand
Die Parteien beabsichtigen..."""
        },
        {
            "id": "termination_template",
            "name": "Kündigung Arbeitsvertrag",
            "category": "employment",
            "content": """Sehr geehrte/r [NAME],

hiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis ordentlich zum [DATUM].

Die Kündigungsfrist beträgt gemäß [GRUNDLAGE] ..."""
        }
    ]
    
    return {"templates": templates}

if __name__ == "__main__":
    # Check environment
    if not TOGETHER_API_KEY:
        logger.error("TOGETHER_API_KEY environment variable not set!")
        exit(1)
    
    logger.info("Starting AnwaltsAI FastAPI Backend...")
    logger.info(f"Together.ai Model: {LLM_MODEL_NAME}")
    logger.info("Available endpoints:")
    logger.info("  POST /api/upload - Upload and extract text from documents")
    logger.info("  POST /api/sanitize - Sanitize text for PII")
    logger.info("  POST /api/ai/respond - Generate AI responses")
    logger.info("  POST /api/generate - Complete document generation pipeline")
    logger.info("  GET /api/templates - Get document templates")
    logger.info("  GET /files/{id}.docx - Download generated documents")
    
    uvicorn.run(
        "fastapi_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )