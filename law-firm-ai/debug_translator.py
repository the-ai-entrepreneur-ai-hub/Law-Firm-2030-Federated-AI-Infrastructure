#!/usr/bin/env python3
"""
Debug Translation Service for Law Firm AI
Provides real-time monitoring and German-to-English translation for debugging purposes.
This is an independent feature that doesn't interfere with core functionality.
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from together import Together
import json

class DebugTranslator:
    """
    Independent translation and debugging service for monitoring the law firm AI.
    Translates German content to English for easier debugging and monitoring.
    """
    
    def __init__(self, together_api_key: str):
        self.client = Together(api_key=together_api_key)
        self.logger = logging.getLogger(__name__)
        
        # Store processing sessions for debugging
        self.debug_sessions = {}
        
        # German legal terms to English mapping for quick translation
        self.legal_terms_mapping = {
            # Common German legal terms
            "Rechtsanwalt": "Lawyer/Attorney",
            "Mandant": "Client", 
            "Kläger": "Plaintiff",
            "Beklagte": "Defendant", 
            "Amtsgericht": "Local Court",
            "Landgericht": "Regional Court",
            "Bundesgerichtshof": "Federal Court of Justice",
            "Klageerhebung": "Filing a Lawsuit",
            "Unterlassungserklärung": "Cease and Desist Declaration",
            "Schadensersatz": "Damages/Compensation",
            "Urheberrechtsverletzung": "Copyright Infringement",
            "Arbeitsrecht": "Labor Law",
            "Bürgerliches Gesetzbuch": "Civil Code",
            "Ersteinschätzung": "Initial Assessment",
            "Rechtslage": "Legal Situation",
            "Anspruchsgrundlage": "Legal Basis for Claim",
            "Erfolgsaussichten": "Chances of Success",
            "Verjährung": "Statute of Limitations",
            "Prozesskostenhilfe": "Legal Aid",
            "Verzugszinsen": "Default Interest",
            "außerordentliche Kündigung": "Extraordinary Termination",
            "Entgeltfortzahlungsanspruch": "Continued Payment Claim",
            "Verwertungsrechte": "Exploitation Rights",
            "Lizenzschaden": "License Damage",
            "entgangener Gewinn": "Lost Profit"
        }
    
    def translate_text(self, german_text: str, context: str = "legal") -> str:
        """
        Translate German text to English using Together AI.
        
        Args:
            german_text: The German text to translate
            context: Context for translation (legal, general, etc.)
            
        Returns:
            English translation
        """
        try:
            # First, do quick replacement of known legal terms
            translated_text = german_text
            for german_term, english_term in self.legal_terms_mapping.items():
                translated_text = re.sub(
                    rf'\b{re.escape(german_term)}\b', 
                    f"{english_term}", 
                    translated_text, 
                    flags=re.IGNORECASE
                )
            
            # For longer texts, use AI translation
            if len(german_text) > 100:
                prompt = f"""Translate the following German legal text to English. 
Maintain the structure and legal terminology accuracy.
Be precise with legal concepts and German legal system terms.

German text:
{german_text}

English translation:"""

                response = self.client.chat.completions.create(
                    model="meta-llama/Llama-3.2-3B-Instruct-Turbo",  # Faster model for translation
                    messages=[
                        {"role": "system", "content": "You are a professional German-to-English translator specializing in legal documents."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1  # Low temperature for accurate translation
                )
                
                ai_translation = response.choices[0].message.content.strip()
                return ai_translation
            else:
                return translated_text
                
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            # Fallback to basic term replacement
            return translated_text
    
    def create_debug_session(self, processing_id: str, filename: str) -> Dict[str, Any]:
        """
        Create a new debug session for monitoring a document processing.
        
        Args:
            processing_id: Unique identifier for the processing session
            filename: Name of the file being processed
            
        Returns:
            Debug session data
        """
        debug_session = {
            "processing_id": processing_id,
            "filename": filename,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "translations": {},
            "pii_analysis": {},
            "llm_interaction": {},
            "status": "started"
        }
        
        self.debug_sessions[processing_id] = debug_session
        return debug_session
    
    def log_step(self, processing_id: str, step_name: str, step_data: Dict[str, Any]) -> None:
        """
        Log a processing step with translation for debugging.
        
        Args:
            processing_id: The processing session ID
            step_name: Name of the processing step
            step_data: Data from the processing step
        """
        if processing_id not in self.debug_sessions:
            self.create_debug_session(processing_id, "unknown")
        
        session = self.debug_sessions[processing_id]
        
        # Translate relevant German content
        translated_data = {}
        for key, value in step_data.items():
            if isinstance(value, str) and self._contains_german(value):
                translated_data[f"{key}_english"] = self.translate_text(value)
                translated_data[key] = value  # Keep original
            else:
                translated_data[key] = value
        
        step_entry = {
            "step_name": step_name,
            "timestamp": datetime.now().isoformat(),
            "data": translated_data
        }
        
        session["steps"].append(step_entry)
        self.logger.info(f"Debug step logged: {step_name} for session {processing_id}")
    
    def log_pii_detection(self, processing_id: str, original_text: str, anonymized_text: str, 
                         rehydration_map: Dict[str, str]) -> None:
        """
        Log PII detection with English translation for debugging.
        
        Args:
            processing_id: The processing session ID
            original_text: Original German text
            anonymized_text: Text with PII replaced by placeholders
            rehydration_map: Mapping of placeholders to original PII
        """
        if processing_id not in self.debug_sessions:
            self.create_debug_session(processing_id, "unknown")
        
        session = self.debug_sessions[processing_id]
        
        # Translate original text preview
        original_preview = original_text[:500] + "..." if len(original_text) > 500 else original_text
        original_english = self.translate_text(original_preview)
        
        # Translate anonymized text preview  
        anon_preview = anonymized_text[:500] + "..." if len(anonymized_text) > 500 else anonymized_text
        anon_english = self.translate_text(anon_preview)
        
        # Analyze PII types
        pii_analysis = {}
        pii_samples_english = {}
        
        for placeholder, original_value in rehydration_map.items():
            entity_type = placeholder.split('_')[0]
            if entity_type not in pii_analysis:
                pii_analysis[entity_type] = []
                pii_samples_english[entity_type] = []
            
            pii_analysis[entity_type].append({
                "placeholder": placeholder,
                "original_german": original_value,
                "type": self._get_pii_type_english(entity_type)
            })
            
            # Translate PII samples that might contain German text
            if self._contains_german(original_value):
                english_value = self.translate_text(original_value)
                pii_samples_english[entity_type].append({
                    "placeholder": placeholder,
                    "original_german": original_value,
                    "english_translation": english_value,
                    "type": self._get_pii_type_english(entity_type)
                })
        
        session["pii_analysis"] = {
            "original_text_german": original_preview,
            "original_text_english": original_english,
            "anonymized_text_german": anon_preview,
            "anonymized_text_english": anon_english,
            "entities_found": len(rehydration_map),
            "pii_by_type": pii_analysis,
            "pii_samples_english": pii_samples_english,
            "total_text_length": len(original_text)
        }
    
    def log_llm_interaction(self, processing_id: str, input_text: str, llm_response: str) -> None:
        """
        Log LLM interaction with translation for debugging.
        
        Args:
            processing_id: The processing session ID
            input_text: Text sent to LLM (anonymized)
            llm_response: Response from LLM
        """
        if processing_id not in self.debug_sessions:
            self.create_debug_session(processing_id, "unknown")
        
        session = self.debug_sessions[processing_id]
        
        # Translate LLM input and output
        input_preview = input_text[:300] + "..." if len(input_text) > 300 else input_text
        input_english = self.translate_text(input_preview)
        
        response_english = self.translate_text(llm_response)
        
        session["llm_interaction"] = {
            "input_text_german": input_preview,
            "input_text_english": input_english,
            "llm_response_german": llm_response,
            "llm_response_english": response_english,
            "input_length": len(input_text),
            "response_length": len(llm_response),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_debug_session(self, processing_id: str) -> Optional[Dict[str, Any]]:
        """
        Get debug session data.
        
        Args:
            processing_id: The processing session ID
            
        Returns:
            Debug session data or None if not found
        """
        return self.debug_sessions.get(processing_id)
    
    def get_all_sessions(self) -> Dict[str, Any]:
        """
        Get all debug sessions.
        
        Returns:
            All debug sessions
        """
        return self.debug_sessions
    
    def _contains_german(self, text: str) -> bool:
        """
        Check if text contains German content.
        
        Args:
            text: Text to check
            
        Returns:
            True if text likely contains German
        """
        # Simple heuristic: check for German legal terms or umlauts
        german_indicators = ['ä', 'ö', 'ü', 'ß', 'Ä', 'Ö', 'Ü']
        german_words = ['der', 'die', 'das', 'und', 'oder', 'mit', 'von', 'zu', 'bei', 'nach']
        
        for indicator in german_indicators:
            if indicator in text:
                return True
        
        words = text.lower().split()
        german_word_count = sum(1 for word in words if word in german_words)
        
        # If more than 10% of words are common German words, consider it German
        return len(words) > 3 and german_word_count / len(words) > 0.1
    
    def _get_pii_type_english(self, entity_type: str) -> str:
        """
        Get English description of PII entity type.
        
        Args:
            entity_type: The entity type code
            
        Returns:
            English description
        """
        type_mapping = {
            "PERSON": "Person Name",
            "ORG": "Organization",
            "LOC": "Location",
            "MISC": "Miscellaneous Entity",
            "DATE": "Date",
            "TIME": "Time",
            "MONEY": "Monetary Amount",
            "PERCENT": "Percentage",
            "EMAIL": "Email Address",
            "PHONE": "Phone Number",
            "IBAN": "Bank Account (IBAN)",
            "BIC": "Bank Identifier Code",
            "STEUER": "Tax ID",
            "USTID": "VAT ID",
            "ADDRESS": "Address",
            "POSTCODE": "Postal Code"
        }
        
        return type_mapping.get(entity_type, f"Unknown Type ({entity_type})")