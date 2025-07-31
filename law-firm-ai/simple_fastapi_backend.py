#!/usr/bin/env python3
"""
Simple FastAPI Backend for AnwaltsAI - Basic Implementation
Testing version without complex dependencies
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import io

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# PDF generation imports
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("ReportLab not available - PDF generation disabled")

# Import Together.ai and system prompts
try:
    import together
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False
    logging.warning("Together.ai library not available - using mock responses")

try:
    from system_prompts import GermanLegalPrompts, DocumentType, TOGETHER_AI_CONFIG
    PROMPTS_AVAILABLE = True
except ImportError:
    PROMPTS_AVAILABLE = False
    logging.warning("System prompts not available - using basic prompts")

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Together.ai client
together_client = None
together_api_key = None
if TOGETHER_AVAILABLE:
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        together_api_key = api_key
        together_client = True  # Flag to indicate Together.ai is available
        logger.info("Together.ai client initialized successfully")
    else:
        logger.warning("TOGETHER_API_KEY not found in environment variables")
else:
    logger.warning("Together.ai library not installed - install with: pip install together")

# In-memory storage for generated documents (for PDF generation)
# In production, you'd use a database
generated_documents = {}

# Initialize FastAPI app
app = FastAPI(
    title="AnwaltsAI Backend API",
    description="Simple legal document processing pipeline",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
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

class AIResponseResponse(BaseModel):
    model_config = {'protected_namespaces': ()}
    
    ai_response: str
    processing_time: float
    tokens_used: Optional[int] = None
    model_used: str
    success: bool

class GenerateDocumentRequest(BaseModel):
    text: Optional[str] = Field(None, description="Direct text input")
    context: Optional[str] = Field(None, description="Additional context")

class DocumentGenerationResponse(BaseModel):
    generated_doc: str
    sanitized_input: str
    entities_removed: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]
    success: bool

def replace_placeholders_with_natural_language(sanitized_text: str) -> str:
    """
    Replace technical PII placeholders with natural German terms to prevent information leakage
    """
    import re
    
    replacements = {
        r'\[PER_\d+\]': 'eine Person',
        r'\[PERSON_\d+\]': 'eine Person', 
        r'\[STEUER_ID_\d+\]': 'eine Steuernummer',
        r'\[TAX_ID_\d+\]': 'eine Steuernummer',
        r'\[IBAN_\d+\]': 'eine Bankverbindung',
        r'\[PLZ_\d+\]': 'eine Postleitzahl',
        r'\[TELEFON_\w*_\d+\]': 'eine Telefonnummer',
        r'\[PHONE_\d+\]': 'eine Telefonnummer',
        r'\[EMAIL_\d+\]': 'eine E-Mail-Adresse',
        r'\[ORG_\d+\]': 'eine Organisation',
        r'\[LOC_\d+\]': 'ein Ort',
        r'\[LOCATION_\d+\]': 'ein Ort',
        r'\[AKTENZEICHEN_\w*_\d+\]': 'ein Aktenzeichen',
        r'\[AKTENZEICHEN_\d+\]': 'ein Aktenzeichen',
        r'\[CASE_NUMBER_\d+\]': 'ein Aktenzeichen',
        r'\[DATE_\d+\]': 'ein Datum',
        r'\[AMOUNT_\d+\]': 'ein Betrag'
    }
    
    for pattern, replacement in replacements.items():
        sanitized_text = re.sub(pattern, replacement, sanitized_text, flags=re.IGNORECASE)
    
    return sanitized_text

# Document cleaning and formatting function
def clean_and_format_document(text: str) -> str:
    """
    Clean document text to remove Markdown formatting and improve readability
    """
    if not text:
        return text
    
    # Remove common Markdown patterns
    import re
    
    # Remove bold/italic markdown (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__ -> bold
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_ -> italic
    
    # Remove header markdown (### Header -> Header)
    text = re.sub(r'^#{1,6}\s*(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Remove code blocks and inline code
    text = re.sub(r'```[\s\S]*?```', '', text)      # Remove code blocks
    text = re.sub(r'`([^`]+)`', r'\1', text)        # `code` -> code
    
    # Remove list markdown and replace with clean formatting
    text = re.sub(r'^[\s]*[-*+]\s+', '• ', text, flags=re.MULTILINE)  # - item -> • item
    
    # Clean up excessive whitespace but preserve paragraph structure
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    text = re.sub(r'[ \t]+', ' ', text)     # Multiple spaces/tabs -> single space
    
    # Ensure proper line endings for legal document sections
    text = re.sub(r'([.!?])\s*\n([A-ZÄÖÜ])', r'\1\n\n\2', text)  # Add space after sentences starting new paragraphs
    
    return text.strip()

# PDF generation function with professional formatting
def generate_pdf(document_text: str, title: str = "Rechtsdokument") -> bytes:
    """
    Generate a professional German legal PDF with page numbers and branding
    """
    if not PDF_AVAILABLE:
        raise Exception("PDF generation not available - ReportLab not installed")
    
    from reportlab.platypus import PageTemplate, Frame, BaseDocTemplate, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.platypus import KeepTogether
    
    # Create a BytesIO buffer to hold the PDF
    buffer = io.BytesIO()
    
    # Custom document class with headers and page numbers
    class GermanLegalDocument(BaseDocTemplate):
        def __init__(self, filename, **kwargs):
            BaseDocTemplate.__init__(self, filename, **kwargs)
            
            # Define frame for content (leaving space for header and footer)
            frame = Frame(
                72, 100,  # x, y (left margin, bottom margin + footer space)
                A4[0] - 144, A4[1] - 200,  # width, height (page width - margins, page height - header/footer)
                leftPadding=0, rightPadding=0,
                topPadding=0, bottomPadding=0
            )
            
            # Create page template
            template = PageTemplate(id='normal', frames=[frame])
            template.beforeDrawPage = self.add_page_decorations
            self.addPageTemplates([template])
        
        def add_page_decorations(self, canvas, doc):
            """Add header with logo area and footer with page numbers"""
            # Save the current state
            canvas.saveState()
            
            # Header area - "Anwalts KI" in italics with decorative elements
            canvas.setFont("Times-Italic", 14)
            canvas.setFillColor(colors.darkblue)
            
            # Add "Anwalts KI" in header
            header_text = "Anwalts KI"
            text_width = canvas.stringWidth(header_text, "Times-Italic", 14)
            x_center = A4[0] / 2 - text_width / 2
            canvas.drawString(x_center, A4[1] - 50, header_text)
            
            # Add decorative line under header
            canvas.setStrokeColor(colors.darkblue)
            canvas.setLineWidth(1)
            canvas.line(72, A4[1] - 65, A4[0] - 72, A4[1] - 65)
            
            # Add lawyer icon placeholder (scales/justice symbol using text)
            canvas.setFont("Times-Roman", 12)
            canvas.setFillColor(colors.darkblue)
            icon_text = "⚖"  # Justice scales symbol
            try:
                icon_width = canvas.stringWidth(icon_text, "Times-Roman", 12)
                canvas.drawString(x_center - icon_width - 10, A4[1] - 50, icon_text)
            except:
                # Fallback if symbol not available
                canvas.drawString(x_center - 30, A4[1] - 50, "[§]")
            
            # Footer with page numbers
            canvas.setFont("Times-Roman", 10)
            canvas.setFillColor(colors.black)
            
            # Page number
            page_num = canvas.getPageNumber()
            page_text = f"Seite {page_num}"
            page_width = canvas.stringWidth(page_text, "Times-Roman", 10)
            canvas.drawString(A4[0] - 72 - page_width, 50, page_text)
            
            # Add footer line
            canvas.setStrokeColor(colors.gray)
            canvas.setLineWidth(0.5)
            canvas.line(72, 70, A4[0] - 72, 70)
            
            # Restore the state
            canvas.restoreState()
    
    # Create the document
    doc = GermanLegalDocument(buffer, pagesize=A4)
    
    # Get styles and create custom German legal styles
    styles = getSampleStyleSheet()
    
    # Document title style
    title_style = ParagraphStyle(
        'GermanTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        spaceAfter=30,
        spaceBefore=20,
        alignment=TA_CENTER,
        fontName='Times-Bold'
    )
    
    # Main body style for German legal text
    body_style = ParagraphStyle(
        'GermanBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=12,
        leading=15,
        fontName='Times-Roman',
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0
    )
    
    # Section heading style (for §1, §2, etc.)
    section_style = ParagraphStyle(
        'GermanSection',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.darkblue,
        spaceAfter=10,
        spaceBefore=20,
        fontName='Times-Bold',
        alignment=TA_LEFT
    )
    
    # Subsection style
    subsection_style = ParagraphStyle(
        'GermanSubsection',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=8,
        fontName='Times-Bold',
        leftIndent=20
    )
    
    # Build the story (content)
    story = []
    
    # Add document title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Process the document text with German legal formatting
    lines = document_text.split('\n')
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        if not line:  # Empty line
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                # Escape HTML characters in text
                paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(paragraph_text, body_style))
                current_paragraph = []
            story.append(Spacer(1, 8))
            
        elif line.startswith('§') or line.startswith('Artikel') or line.startswith('Art.'):
            # German legal sections
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(paragraph_text, body_style))
                current_paragraph = []
            
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, section_style))
            
        elif line.isupper() and len(line) > 5:
            # Major headings
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(paragraph_text, body_style))
                current_paragraph = []
            
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, section_style))
            
        elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) and len(line.split('.')[0]) <= 3:
            # Numbered subsections
            if current_paragraph:
                paragraph_text = ' '.join(current_paragraph)
                paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(paragraph_text, body_style))
                current_paragraph = []
            
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, subsection_style))
            
        else:
            current_paragraph.append(line)
    
    # Add any remaining paragraph
    if current_paragraph:
        paragraph_text = ' '.join(current_paragraph)
        paragraph_text = paragraph_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(paragraph_text, body_style))
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

# Helper function for Together.ai API calls
async def call_together_ai(system_prompt: str, user_prompt: str) -> str:
    """
    Call Together.ai API - REAL AI ONLY, NO MOCK RESPONSES EVER
    """
    logger.info(f"REAL AI CALL: together_client={together_client}, API key available={together_api_key is not None}")
    
    if not together_client or not together_api_key:
        logger.error("Together.ai not properly configured!")
        raise Exception("Together.ai client not available - cannot generate documents without AI")

    try:
        # Use Together.ai client following user's example
        from together import Together
        
        # Set API key via environment (Together client will pick it up automatically)
        import os
        os.environ["TOGETHER_API_KEY"] = together_api_key
        client = Together()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        model_to_use = TOGETHER_AI_CONFIG["model"] if PROMPTS_AVAILABLE else "moonshotai/Kimi-K2-Instruct"
        logger.info(f"Making REAL API call to model: {model_to_use}")
        
        response = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            max_tokens=TOGETHER_AI_CONFIG["max_tokens"] if PROMPTS_AVAILABLE else 2000,
            temperature=TOGETHER_AI_CONFIG["temperature"] if PROMPTS_AVAILABLE else 0.2,
            top_p=TOGETHER_AI_CONFIG["top_p"] if PROMPTS_AVAILABLE else 0.9
        )
        
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content.strip()
            logger.info(f"REAL AI SUCCESS: Generated {len(content)} characters")
            
            # Double-check it's not somehow a mock response
            if "Mock-Antwort" in content or content.startswith("RECHTSDOKUMENT"):
                logger.error("CRITICAL: AI returned mock-like response!")
                raise Exception("AI returned invalid response format")
            
            return content
        else:
            logger.error("Empty response from Together.ai API")
            raise Exception("Empty response from Together.ai API")
            
    except Exception as e:
        logger.error(f"REAL AI GENERATION FAILED: {e}")
        raise Exception(f"Together.ai API failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AnwaltsAI Simple FastAPI Backend",
        "version": "1.0.0",
        "components": {
            "together_ai": "configured" if os.getenv("TOGETHER_API_KEY") else "missing_key",
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process document (PDF, DOCX, image) with basic text extraction
    """
    start_time = datetime.now()
    
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > 50:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
        
        logger.info(f"Processing uploaded file: {file.filename} ({file_size_mb:.2f}MB)")
        
        # Basic text extraction (simplified)
        extracted_text = ""
        
        if file.content_type == "text/plain":
            extracted_text = file_content.decode('utf-8', errors='ignore')
        elif file.content_type == "application/pdf":
            # Simulate PDF extraction
            extracted_text = f"[PDF Content from {file.filename}]\n\nSehr geehrte Damen und Herren,\n\ndies ist ein Beispieltext aus einem PDF-Dokument. In einem echten System würde hier der tatsächliche PDF-Inhalt extrahiert werden.\n\nMit freundlichen Grüßen"
        else:
            # Try to decode as text
            try:
                extracted_text = file_content.decode('utf-8', errors='ignore')
            except:
                extracted_text = f"[Content from {file.filename}]\n\nDatei wurde hochgeladen, aber der Inhalt konnte nicht als Text interpretiert werden."
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail="Document processing failed")

@app.post("/api/sanitize", response_model=SanitizeResponse)
async def sanitize_text(request: SanitizeRequest):
    """
    Simple PII sanitization (basic patterns)
    """
    start_time = datetime.now()
    
    try:
        text = request.text
        
        if not text or len(text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Text too short or empty")
        
        logger.info("Starting basic PII sanitization")
        
        # Simple PII patterns
        import re
        
        entities_removed = []
        sanitized_text = text
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for i, email in enumerate(emails):
            placeholder = f"[EMAIL_{i+1}]"
            sanitized_text = sanitized_text.replace(email, placeholder)
            entities_removed.append({
                "type": "EMAIL",
                "original": email,
                "replacement": placeholder,
                "confidence": 0.95,
                "detection_method": "regex"
            })
        
        # Phone numbers (German)
        phone_pattern = r'\b(?:\+49|0)\s?\d{2,5}[\s\-]?\d{3,8}\b'
        phones = re.findall(phone_pattern, text)
        for i, phone in enumerate(phones):
            placeholder = f"[PHONE_{i+1}]"
            sanitized_text = sanitized_text.replace(phone, placeholder)
            entities_removed.append({
                "type": "PHONE",
                "original": phone,
                "replacement": placeholder,
                "confidence": 0.90,
                "detection_method": "regex"
            })
        
        # IBAN
        iban_pattern = r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b'
        ibans = re.findall(iban_pattern, text)
        for i, iban in enumerate(ibans):
            placeholder = f"[IBAN_{i+1}]"
            sanitized_text = sanitized_text.replace(iban, placeholder)
            entities_removed.append({
                "type": "IBAN",
                "original": iban,
                "replacement": placeholder,
                "confidence": 0.98,
                "detection_method": "regex"
            })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Basic PII sanitization completed: {len(entities_removed)} entities removed")
        
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
    Generate German legal AI response (mock implementation for testing)
    """
    start_time = datetime.now()
    
    try:
        if not request.sanitized_text or len(request.sanitized_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Sanitized text too short")
        
        logger.info("Generating AI response with Together.ai")
        
        # Replace PII placeholders with natural language to prevent information leakage
        clean_text = replace_placeholders_with_natural_language(request.sanitized_text)
        
        # Use real AI for response generation
        if PROMPTS_AVAILABLE:
            system_prompt, user_prompt = GermanLegalPrompts.get_response_generation_prompt(
                sanitized_email=clean_text,
                context=request.context or ""
            )
        else:
            system_prompt = """Du bist ein erfahrener deutscher Rechtsanwalt. 
            Erstelle eine professionelle, höfliche E-Mail-Antwort auf Deutsch.
            Verwende juristische Fachsprache und gib konkrete rechtliche Hinweise."""
            user_prompt = f"E-Mail-Anfrage: {clean_text}\nKontext: {request.context}"
        
        ai_response = await call_together_ai(system_prompt, user_prompt)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"AI response generated successfully in {processing_time:.2f}s")
        
        return AIResponseResponse(
            ai_response=ai_response,
            processing_time=round(processing_time, 2),
            tokens_used=len(ai_response.split()) * 2,  # Mock token count
            model_used="mock-german-legal-model",
            success=True
        )
        
    except Exception as e:
        logger.error(f"AI response generation failed: {e}")
        raise HTTPException(status_code=500, detail="AI response generation failed")

@app.post("/api/generate", response_model=DocumentGenerationResponse)
async def generate_document(request: GenerateDocumentRequest):
    """
    Complete document generation pipeline - REAL AI ONLY, NO MOCK RESPONSES
    """
    start_time = datetime.now()
    
    try:
        # Step 1: Get input text
        if not request or not request.text:
            raise HTTPException(status_code=400, detail="No input text provided")
        
        raw_text = request.text.strip()
        if len(raw_text) < 5:
            raise HTTPException(status_code=400, detail="Input text too short")
        
        logger.info(f"Processing document generation request: {len(raw_text)} chars")
        
        # Step 2: Determine document type based on context
        document_type = DocumentType.ALLGEMEIN
        if request.context:
            context_lower = request.context.lower()
            if "mahnung" in context_lower or "zahlung" in context_lower:
                document_type = DocumentType.MAHNUNG
            elif "nda" in context_lower or "geheimhaltung" in context_lower:
                document_type = DocumentType.GEHEIMHALTUNG
            elif "kündigung" in context_lower or "beendigung" in context_lower:
                document_type = DocumentType.KUENDIGUNG
            elif "vertrag" in context_lower or "vereinbarung" in context_lower:
                document_type = DocumentType.VERTRAG
            elif "schaden" in context_lower or "ersatz" in context_lower:
                document_type = DocumentType.SCHADENSERSATZ
        
        logger.info(f"Detected document type: {document_type.value}")
        
        # Step 3: Replace PII placeholders and create AI prompts
        clean_text = replace_placeholders_with_natural_language(raw_text)
        
        if PROMPTS_AVAILABLE:
            system_prompt = GermanLegalPrompts.get_system_prompt(
                document_type=document_type,
                context={"legal_area": request.context, "urgent": False}
            )
            user_prompt = GermanLegalPrompts.get_user_prompt(
                user_input=clean_text,
                document_type=document_type
            )
        else:
            system_prompt = """Du bist ein erfahrener deutscher Rechtsanwalt mit 20+ Jahren Erfahrung. 
Erstelle ein vollständiges, professionelles deutsches Rechtsdokument.

WICHTIGE FORMATIERUNGS-REGELN:
- NIEMALS Markdown verwenden (keine **, ##, ***, ___, etc.)
- NIEMALS Sterne (*) oder Hashtags (#) für Formatierung  
- Verwende AUSSCHLIESSLICH Plaintext mit natürlicher Formatierung
- Für Überschriften: Großbuchstaben und Doppelpunkt wie "TITEL:"
- Für Absätze: Leerzeilen zwischen Abschnitten
- Für Listen: Einfache Punkte (•) oder a), b), c)
- KEINE Platzhalter wie [NAME] oder [DATUM]
- Erstelle vollständig ausgefülltes, sofort verwendbares Dokument auf Deutsch"""
            
            user_prompt = f"""Erstelle ein professionelles deutsches Rechtsdokument:

Anfrage: {clean_text}
Kontext: {request.context or 'Allgemeine rechtliche Angelegenheit'}

Das Dokument muss vollständig und sofort verwendbar sein."""

        # Step 4: MANDATORY AI call - no fallbacks allowed
        logger.info("Calling Together.ai API - NO MOCK RESPONSES ALLOWED")
        
        if not together_client or not together_api_key:
            raise HTTPException(status_code=500, detail="Together.ai not properly configured - cannot generate documents without AI")
        
        # Force real AI generation
        raw_ai_response = await call_together_ai(system_prompt, user_prompt)
        
        # Clean and format the document (remove any Markdown that might have slipped through)
        generated_document = clean_and_format_document(raw_ai_response)
        
        # Verify it's not a mock response
        if "Mock-Antwort" in generated_document or "RECHTSDOKUMENT" in generated_document:
            logger.error("Received mock response instead of real AI - this should not happen!")
            raise HTTPException(status_code=500, detail="AI service returned mock response")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Processing stats
        processing_stats = {
            "processing_time": round(processing_time, 2),
            "input_length": len(raw_text),
            "sanitized_length": len(raw_text),  # No PII sanitization in this version
            "output_length": len(generated_document),
            "entities_removed": 0,  # No PII sanitization in this version
            "tokens_used": len(generated_document.split()),
            "document_type": document_type.value,
            "ai_model": TOGETHER_AI_CONFIG["model"] if PROMPTS_AVAILABLE else "moonshotai/Kimi-K2-Instruct",
            "together_ai_used": True,  # Must be true if we reach this point
            "real_ai_generation": True,
            "pdf_available": PDF_AVAILABLE,
            "document_id": str(uuid.uuid4())  # For PDF download
        }
        
        logger.info(f"REAL AI document generation completed in {processing_time:.2f}s, {len(generated_document)} chars")
        
        # Store the document for PDF generation
        document_id = processing_stats["document_id"]
        generated_documents[document_id] = {
            "content": generated_document,
            "title": f"Legal Document - {document_type.value.title()}",
            "created_at": datetime.now(),
            "document_type": document_type.value
        }
        
        return DocumentGenerationResponse(
            generated_doc=generated_document,
            sanitized_input=raw_text,
            entities_removed=[],
            processing_stats=processing_stats,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Real AI document generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Real AI generation failed: {str(e)}")

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
        }
    ]
    
    return {"templates": templates}

@app.get("/api/download-pdf/{document_id}")
async def download_pdf(document_id: str):
    """
    Download generated document as PDF
    """
    try:
        if not PDF_AVAILABLE:
            raise HTTPException(status_code=503, detail="PDF generation not available")
        
        if document_id not in generated_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_info = generated_documents[document_id]
        
        # Generate PDF
        pdf_data = generate_pdf(
            document_text=doc_info["content"],
            title=doc_info["title"]
        )
        
        # Create filename
        timestamp = doc_info["created_at"].strftime("%Y%m%d_%H%M%S")
        doc_type = doc_info["document_type"]
        filename = f"AnwaltsKI_{doc_type}_{timestamp}.pdf"
        
        logger.info(f"Generated PDF for document {document_id}: {filename} ({len(pdf_data)} bytes)")
        
        # Return PDF with proper headers for download
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
            "Content-Length": str(len(pdf_data)),
            "Cache-Control": "no-cache"
        }
        
        return StreamingResponse(
            io.BytesIO(pdf_data),
            media_type="application/pdf",
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

if __name__ == "__main__":
    # Check environment
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        logger.warning("TOGETHER_API_KEY not found - running in mock mode")
    else:
        logger.info("TOGETHER_API_KEY configured")
    
    logger.info("Starting AnwaltsAI Simple FastAPI Backend...")
    logger.info("Available endpoints:")
    logger.info("  POST /api/upload - Upload and extract text from documents")
    logger.info("  POST /api/sanitize - Sanitize text for PII")
    logger.info("  POST /api/ai/respond - Generate AI responses")
    logger.info("  POST /api/generate - Complete document generation pipeline")
    logger.info("  GET /api/templates - Get document templates")
    
    # Find available port
    import socket
    def find_free_port(start_port=8003):
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return start_port
    
    port = find_free_port(8003)
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        "simple_fastapi_backend:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload to prevent conflicts
        log_level="info"
    )