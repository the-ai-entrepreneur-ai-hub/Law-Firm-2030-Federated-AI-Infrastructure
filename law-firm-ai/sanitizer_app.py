# FILE: sanitizer_app.py

import spacy
import re
import requests
import ocrmypdf
import io
import os
import logging
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from together import Together

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    
try:
    import pytesseract
except ImportError:
    pytesseract = None

# --- Initial Setup & Configuration ---

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Configuration for Together AI ---
TOGETHER_API_KEY = "REDACTED"
LLM_MODEL_NAME = "deepseek-ai/DeepSeek-V3"

# Initialize Together client
together_client = Together(api_key=TOGETHER_API_KEY)

# Enhanced German Legal Document Patterns
CUSTOM_PATTERNS = {
    # Financial Information
    'IBAN': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
    'BIC': r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
    'BANK_ACCOUNT': r'\b\d{8,12}\b',
    'STEUER_ID': r'\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b',
    'USTID': r'\bDE\d{9}\b',
    
    # Legal Case Information
    'AKTENZEICHEN': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\b',
    'GESCHAEFTSZAHL': r'\b\d{1,3}\s?[A-Z]{1,3}\s?\d{1,5}\b',
    'GERICHTSAKTENZEICHEN': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\s?[A-Z]{0,3}\b',
    
    # Addresses and Locations
    'PLZ': r'\b\d{5}\b',
    'TELEFON': r'\b(?:\+49|0)\s?\d{2,5}[\s-]?\d{3,8}\b',
    'HANDY': r'\b(?:\+49|0)\s?1\d{2}[\s-]?\d{7,8}\b',
    'FAX': r'\b(?:Fax|fax)\s?[:\.]?\s?(?:\+49|0)\s?\d{2,5}[\s-]?\d{3,8}\b',
    
    # Personal Information
    'GEBURTSDATUM': r'\b\d{1,2}[\.\/]\d{1,2}[\.\/]\d{4}\b',
    'PERSONALAUSWEIS': r'\b\d{10}\b',
    'REISEPASS': r'\b[A-Z]\d{8}\b',
    
    # Email and Web
    'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'WEBSITE': r'\b(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}(?:/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=-]*)?\b',
    
    # Insurance and Medical
    'VERSICHERUNGSNUMMER': r'\b[A-Z]\d{9}\b',
    'KRANKENKASSE': r'\b\d{9}\b',
    
    # License Plates
    'KENNZEICHEN': r'\b[A-Z]{1,3}[-\s]?[A-Z]{1,2}\s?\d{1,4}[EH]?\b',
    
    # Amounts and Currency
    'BETRAG_EUR': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:EUR|€|Euro)\b',
    'BETRAG_NUMMER': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b(?=\s?(?:EUR|€|Euro))'
}

NLP = spacy.load("de_core_news_sm")
app.logger.info("spaCy German model 'de_core_news_sm' loaded successfully.")

# --- Helper Functions ---

def perform_ocr(mime_type, file_bytes):
    """Optimized OCR using ocrmypdf for PDFs with direct text extraction."""
    app.logger.info(f"Performing OCR for mime type: {mime_type}")
    start_time = datetime.now()

    if mime_type == 'application/pdf':
        try:
            input_pdf = io.BytesIO(file_bytes)
            output_pdf = io.BytesIO()
            
            # Use OCRmyPDF with optimized settings for speed
            ocrmypdf.ocr(
                input_pdf,
                output_pdf,
                language='deu',
                force_ocr=True,
                optimize=1,  # Basic optimization for speed
                jpeg_quality=85,  # Balance quality/speed
                png_quality=85,
                fast_web_view=1,  # Optimize for streaming
                clean=False,  # Skip cleaning for speed
                deskew=False,  # Skip deskewing for speed
                remove_background=False,  # Skip background removal
                progress_bar=False,
                quiet=True
            )
            
            # Extract text directly from the OCRed PDF
            if pdfplumber is None:
                app.logger.error("pdfplumber not available for text extraction")
                return None
            
            # Write OCRed PDF to temporary file for text extraction
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(output_pdf.getvalue())
                temp_path = temp_file.name
            
            try:
                # Extract text using pdfplumber
                text = ""
                with pdfplumber.open(temp_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                
                os.unlink(temp_path)  # Clean up temp file
                
                total_time = (datetime.now() - start_time).total_seconds()
                app.logger.info(f"OCRmyPDF processing completed in {total_time:.2f}s")
                return text.strip()
                
            except Exception as e:
                app.logger.error(f"Text extraction from OCRed PDF failed: {e}")
                os.unlink(temp_path)  # Ensure cleanup
                return None

        except Exception as e:
            app.logger.error(f"OCRmyPDF processing failed: {e}")
            return None

    elif mime_type.startswith('image/'):
        try:
            if pytesseract is None:
                app.logger.error("pytesseract not available for image OCR")
                return None
                
            image = Image.open(io.BytesIO(file_bytes))
            
            # Use pytesseract with German language and optimized settings
            custom_config = r'--oem 3 --psm 6 -l deu'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            total_time = (datetime.now() - start_time).total_seconds()
            app.logger.info(f"Tesseract OCR completed in {total_time:.2f}s")
            return text.strip()
            
        except Exception as e:
            app.logger.error(f"Tesseract OCR failed: {e}")
            return None

    return None
def anonymize_text(text):
    """Enhanced anonymization with advanced pattern matching and entity recognition."""
    app.logger.info("Starting advanced anonymization process...")
    start_time = datetime.now()
    
    # Create a copy for processing
    anonymized_text = text
    rehydration_map = {}
    placeholder_counts = {}
    
    # Step 1: spaCy Named Entity Recognition
    app.logger.info("Processing with spaCy NER...")
    doc = NLP(text)
    
    # Process entities in reverse order to maintain text positions
    for ent in reversed(doc.ents):
        label = ent.label_
        entity_text = ent.text.strip()
        
        # Skip if entity is too short or contains only punctuation
        if len(entity_text) < 2 or entity_text.isspace():
            continue
            
        placeholder_counts[label] = placeholder_counts.get(label, 0) + 1
        placeholder = f"[{label}_{placeholder_counts[label]}]"
        rehydration_map[placeholder] = entity_text
        
        # Replace in text
        anonymized_text = anonymized_text[:ent.start_char] + placeholder + anonymized_text[ent.end_char:]
    
    # Step 2: Custom regex patterns for German legal documents
    app.logger.info("Applying custom German legal patterns...")
    for label, pattern in CUSTOM_PATTERNS.items():
        matches = list(re.finditer(pattern, anonymized_text, re.IGNORECASE))
        
        # Process matches in reverse order
        for match in reversed(matches):
            original_value = match.group(0)
            
            # Skip if already anonymized
            if original_value in rehydration_map.values():
                continue
                
            # Create unique placeholder
            placeholder_counts[label] = placeholder_counts.get(label, 0) + 1
            placeholder = f"[{label}_{placeholder_counts[label]}]"
            rehydration_map[placeholder] = original_value
            
            # Replace in text
            start, end = match.span()
            anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]
    
    # Step 3: Advanced pattern matching for German names and addresses
    app.logger.info("Applying advanced German name and address patterns...")
    
    # German street patterns
    street_patterns = [
        r'\b[A-Z][a-zäöüß]+(?:straße|str\.|gasse|platz|weg|allee|ring|damm)\s+\d{1,4}[a-z]?\b',
        r'\b[A-Z][a-zäöüß]+(?:-[A-Z][a-zäöüß]+)*(?:straße|str\.|gasse|platz|weg|allee|ring|damm)\s+\d{1,4}[a-z]?\b'
    ]
    
    for pattern in street_patterns:
        matches = list(re.finditer(pattern, anonymized_text, re.IGNORECASE))
        for match in reversed(matches):
            original_value = match.group(0)
            if original_value not in rehydration_map.values():
                placeholder_counts['STRASSE'] = placeholder_counts.get('STRASSE', 0) + 1
                placeholder = f"[STRASSE_{placeholder_counts['STRASSE']}]"
                rehydration_map[placeholder] = original_value
                start, end = match.span()
                anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]
    
    # Step 4: Store anonymization metadata
    anonymization_metadata = {
        'timestamp': datetime.now().isoformat(),
        'total_entities': len(rehydration_map),
        'entity_types': list(placeholder_counts.keys()),
        'processing_time': (datetime.now() - start_time).total_seconds()
    }
    
    app.logger.info(f"Anonymization completed in {anonymization_metadata['processing_time']:.2f}s")
    app.logger.info(f"Found {anonymization_metadata['total_entities']} entities of types: {', '.join(anonymization_metadata['entity_types'])}")
    
    return anonymized_text, rehydration_map

def call_llm(anonymized_text):
    """Enhanced LLM call using Together client with DeepSeek-V3."""
    app.logger.info(f"Sending request to Together AI with model: {LLM_MODEL_NAME}...")
    start_time = datetime.now()

    # Enhanced system prompt for German legal analysis
    system_prompt = """Sie sind ein erfahrener deutscher Rechtsassistent mit Expertise in verschiedenen Rechtsgebieten. \nIhre Aufgabe ist es, rechtliche Dokumente zu analysieren und eine strukturierte Ersteinschätzung für einen Anwalt zu erstellen.\n\nWichtige Hinweise:\n- Der Text wurde anonymisiert - Platzhalter wie [PER_1], [STRASSE_1], [AKTENZEICHEN_1] etc. repräsentieren personenbezogene Daten\n- Verwenden Sie diese Platzhalter in Ihrer Antwort, als wären es die ursprünglichen Namen/Daten\n- Fokussieren Sie sich auf rechtliche Aspekte und praktische Handlungsempfehlungen\n- Berücksichtigen Sie deutsche Gesetze und Verfahren"""

    # Enhanced user prompt with better structure
    user_prompt = f"""Analysieren Sie bitte das folgende rechtliche Dokument:\n\n<Dokument>\n{anonymized_text}\n</Dokument>\n\nBitte erstellen Sie eine strukturierte Analyse nach folgendem Schema:\n\n**📋 BETREFF:** \n(Eindeutiger, prägnanter Betreff für diesen Fall)\n\n**📄 1. SACHVERHALT:**\n• (Kernfakte in Stichpunkten)\n• (Beteiligte Parteien mit Platzhaltern)\n• (Relevante Daten und Fristen)\n\n**⚖️ 2. RECHTLICHE BEWERTUNG:**\n• Rechtsgebiet: (z.B. Zivilrecht, Arbeitsrecht, etc.)\n• Rechtslage: (Kurze Einschätzung der Rechtslage)\n• Risiken: (Potenzielle Risiken oder Probleme)\n• Erfolgsaussichten: (Wenn zutreffend)\n\n**🎯 3. EMPFOHLENE MASSNAHMEN:**\n• Sofortige Schritte: (Was muss sofort getan werden?)\n• Fristen: (Welche Fristen sind zu beachten?)\n• Weitere Unterlagen: (Was wird noch benötigt?)\n• Mandantenkontakt: (Gesprächsbedarf mit [PER_X])\n\n**⚠️ 4. BESONDERE HINWEISE:**\n(Wichtige Punkte, die besondere Aufmerksamkeit erfordern)\n\nBitte bleiben Sie bei der Analyse sachlich und verwenden Sie die Platzhalter für personenbezogene Daten."""

    try:
        # Use Together client for streaming response
        response = together_client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            stream=False  # Non-streaming for easier handling
        )
        
        llm_output = response.choices[0].message.content
        
        processing_time = (datetime.now() - start_time).total_seconds()
        app.logger.info(f"LLM processing completed in {processing_time:.2f}s")
        
        return llm_output.strip()
        
    except Exception as e:
        app.logger.error(f"Together AI request failed: {str(e)}")
        raise

def rehydrate_response(llm_response, rehydration_map):
    """Enhanced rehydration with security logging and validation."""
    app.logger.info("Starting rehydration process...")
    start_time = datetime.now()
    
    rehydrated_text = llm_response
    replacements_made = 0
    
    # Sort placeholders by length (longest first) to avoid partial replacements
    sorted_placeholders = sorted(rehydration_map.keys(), key=len, reverse=True)
    
    for placeholder in sorted_placeholders:
        if placeholder in rehydrated_text:
            original_value = rehydration_map[placeholder]
            rehydrated_text = rehydrated_text.replace(placeholder, original_value)
            replacements_made += 1
            app.logger.debug(f"Replaced {placeholder} with original data")
    
    processing_time = (datetime.now() - start_time).total_seconds()
    app.logger.info(f"Rehydration completed in {processing_time:.2f}s")
    app.logger.info(f"Made {replacements_made} replacements out of {len(rehydration_map)} possible")
    
    # Security check: ensure no placeholders remain
    remaining_placeholders = re.findall(r'\[[A-Z_]+_\d+\]', rehydrated_text)
    if remaining_placeholders:
        app.logger.warning(f"Warning: {len(remaining_placeholders)} placeholders remain unreplaced")
    
    return rehydrated_text

# --- API Endpoint ---

@app.route('/process-document', methods=['POST'])
def process_document_endpoint():
    """Enhanced main endpoint with comprehensive document processing pipeline."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Initialize processing metrics
    start_time = datetime.now()
    processing_id = hashlib.md5(f"{file.filename}_{start_time.isoformat()}".encode()).hexdigest()[:8]
    
    try:
        app.logger.info(f"[{processing_id}] Starting document processing: {file.filename} (MIME: {file.mimetype})")
        
        # Validate file
        file_bytes = file.read()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        app.logger.info(f"[{processing_id}] File size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 50:  # 50MB limit
            return jsonify({"error": "File too large. Maximum size is 50MB."}), 413
        
        # Step 1: OCR Processing
        app.logger.info(f"[{processing_id}] Step 1: OCR processing started")
        ocr_start = datetime.now()
        raw_text = perform_ocr(file.mimetype, file_bytes)
        ocr_time = (datetime.now() - ocr_start).total_seconds()
        
        if raw_text is None:
            return jsonify({"error": f"Unsupported file type: {file.mimetype}"}), 415
        
        text_length = len(raw_text)
        app.logger.info(f"[{processing_id}] OCR completed in {ocr_time:.2f}s, extracted {text_length} characters")
        
        # Step 2: Anonymization
        app.logger.info(f"[{processing_id}] Step 2: Anonymization started")
        anon_start = datetime.now()
        anonymized_text, rehydration_map = anonymize_text(raw_text)
        anon_time = (datetime.now() - anon_start).total_seconds()
        
        entities_found = len(rehydration_map)
        app.logger.info(f"[{processing_id}] Anonymization completed in {anon_time:.2f}s, found {entities_found} entities")
        
        # Step 3: LLM Processing
        app.logger.info(f"[{processing_id}] Step 3: LLM analysis started")
        llm_start = datetime.now()
        llm_response = call_llm(anonymized_text)
        llm_time = (datetime.now() - llm_start).total_seconds()
        
        app.logger.info(f"[{processing_id}] LLM analysis completed in {llm_time:.2f}s")
        
        # Step 4: Rehydration
        app.logger.info(f"[{processing_id}] Step 4: Rehydration started")
        rehydration_start = datetime.now()
        final_response = rehydrate_response(llm_response, rehydration_map)
        rehydration_time = (datetime.now() - rehydration_start).total_seconds()
        
        # Calculate total processing time
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare detailed PII information
        pii_details = {
            "entities_found": entities_found,
            "entity_types": list(set([key.split('_')[0] for key in rehydration_map.keys()])),
            "entity_breakdown": {},
            "sample_entities": {}
        }
        
        # Count entities by type and provide samples (first 3 per type)
        for placeholder, original_value in rehydration_map.items():
            entity_type = placeholder.split('_')[0]
            if entity_type not in pii_details["entity_breakdown"]:
                pii_details["entity_breakdown"][entity_type] = 0
                pii_details["sample_entities"][entity_type] = []
            
            pii_details["entity_breakdown"][entity_type] += 1
            
            # Add sample (limit to 3 per type for display)
            if len(pii_details["sample_entities"][entity_type]) < 3:
                pii_details["sample_entities"][entity_type].append({
                    "placeholder": placeholder,
                    "original": original_value[:30] + "..." if len(original_value) > 30 else original_value
                })
        
        # Prepare comprehensive response
        processing_stats = {
            "processing_id": processing_id,
            "file_size_mb": round(file_size_mb, 2),
            "text_length": text_length,
            "entities_found": entities_found,
            "timing": {
                "ocr_time": round(ocr_time, 2),
                "anonymization_time": round(anon_time, 2),
                "llm_time": round(llm_time, 2),
                "rehydration_time": round(rehydration_time, 2),
                "total_time": round(total_time, 2)
            },
            "timestamp": start_time.isoformat()
        }
        
        app.logger.info(f"[{processing_id}] Processing completed successfully in {total_time:.2f}s")
        
        return jsonify({
            "success": True,
            "final_response": final_response,
            "processing_stats": processing_stats,
            "process_details": {
                "original_text_preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
                "anonymized_text_preview": anonymized_text[:500] + "..." if len(anonymized_text) > 500 else anonymized_text,
                "pii_details": pii_details,
                "llm_response_preview": llm_response[:300] + "..." if len(llm_response) > 300 else llm_response
            },
            "debug_data": {
                "original_text": raw_text,
                "anonymized_text": anonymized_text,
                "rehydration_map": rehydration_map,
                "llm_response": llm_response
            } if app.debug else None,
            "message": f"Document processed successfully in {total_time:.2f} seconds"
        })

    except requests.exceptions.ReadTimeout:
        error_msg = "The AI model took too long to respond. This can happen with very large documents."
        app.logger.error(f"[{processing_id}] Timeout error: {error_msg}")
        return jsonify({"error": error_msg}), 504
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API request to Together AI failed: {str(e)}"
        app.logger.error(f"[{processing_id}] API error: {error_msg}", exc_info=True)
        return jsonify({"error": f"An API error occurred. Check your API key and model name. Details: {str(e)}"}), 502
        
    except Exception as e:
        error_msg = f"An internal error occurred: {str(e)}"
        app.logger.error(f"[{processing_id}] Internal error: {error_msg}", exc_info=True)
        return jsonify({"error": error_msg}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with system information."""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "Advanced OCR with parallel processing",
            "Enhanced German legal document anonymization",
            "Comprehensive entity recognition",
            "Secure PII handling",
            "Detailed processing metrics"
        ],
        "timestamp": datetime.now().isoformat()
    })

# This endpoint is now defined above in the previous edit

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
