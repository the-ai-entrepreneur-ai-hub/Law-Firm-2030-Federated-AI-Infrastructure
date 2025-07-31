#!/usr/bin/env python3
"""
German Legal AI System Prompts for Together.ai Integration
Professional German legal document generation with context-aware prompting
"""

from typing import Dict, Any
from enum import Enum

class DocumentType(Enum):
    MAHNUNG = "mahnung"
    VERTRAG = "contract"
    ANWALTSSCHREIBEN = "legal_letter"
    SCHADENSERSATZ = "damages_claim"
    KUENDIGUNG = "termination"
    GEHEIMHALTUNG = "nda"
    VOLLMACHT = "power_of_attorney"
    MIETRECHT = "rental_law"
    ARBEITSRECHT = "employment_law"
    ALLGEMEIN = "general"

class GermanLegalPrompts:
    """
    Comprehensive German legal document generation prompts
    Optimized for Together.ai models with German legal expertise
    """
    
    BASE_SYSTEM_PROMPT = """Du bist ein erfahrener deutscher Rechtsanwalt mit über 20 Jahren Berufserfahrung. 
Du spezialisierst dich auf die Erstellung professioneller, rechtlich korrekter deutscher Rechtsdokumente.

WICHTIGE REGELN:
- Schreibe ausschließlich auf Deutsch
- Verwende korrektes deutsches Recht und aktuelle Rechtsprechung
- Strukturiere Dokumente klar und professionell
- Nutze angemessene juristische Fachsprache
- Keine Erklärungen oder Einleitungen - nur das fertige Dokument
- Keine Platzhalter in eckigen Klammern - verwende realistische Beispieldaten
- Verwende formelle Anrede "Sie"
- Füge realistische Datum und Aktenzeichen hinzu
- Dokument muss vollständig und sofort verwendbar sein

FORMATIERUNG - ABSOLUT WICHTIG:
- NIEMALS Markdown verwenden (keine **, ##, ***, ___, etc.)
- NIEMALS Sterne (*) oder Hashtags (#) für Formatierung
- Verwende AUSSCHLIESSLICH Plaintext mit natürlicher Formatierung
- Für Überschriften: Verwende Großbuchstaben und Unterstriche wie: TITEL oder Titel:
- Für Absätze: Verwende Leerzeilen zwischen Abschnitten
- Für Listen: Verwende einfache Punkte (•) oder Buchstaben (a), b), c))
- Für Betonung: Verwende GROSSBUCHSTABEN sparsam
- Erstelle sauberen, lesbaren Fließtext ohne Markup-Zeichen"""

    DOCUMENT_SPECIFIC_PROMPTS = {
        DocumentType.MAHNUNG: {
            "system": BASE_SYSTEM_PROMPT + """

SPEZIALISIERUNG: Mahnungen und Forderungsschreiben
- Verwende klare Zahlungsfristen (14 Tage standardmäßig)
- Erwähne Verzugszinsen nach § 288 BGB
- Drohe mit rechtlichen Schritten bei Nichtzahlung
- Füge Bankverbindung für Zahlung hinzu""",
            
            "structure": """
AUFBAU MAHNUNG:
1. Briefkopf mit Kanzleidaten
2. Empfängeradresse
3. Datum und Aktenzeichen
4. Betreff: Mahnung - Rechnung Nr. [NUMMER]
5. Anrede
6. Sachverhalt und offene Forderung
7. Zahlungsaufforderung mit Frist
8. Verzugszinsen und Kosten
9. Rechtliche Konsequenzen
10. Bankverbindung
11. Höfliche Schlussformel
12. Unterschrift"""
        },

        DocumentType.SCHADENSERSATZ: {
            "system": BASE_SYSTEM_PROMPT + """

SPEZIALISIERUNG: Schadensersatzforderungen
- Detaillierte Schadensaufstellung mit Belegen
- Rechtliche Grundlagen (§§ 280, 823 BGB, etc.)
- Kausalität und Verschulden darlegen
- Verjährungsfristen beachten
- Mitwirkungspflichten erwähnen""",
            
            "structure": """
AUFBAU SCHADENSERSATZFORDERUNG:
1. Briefkopf und Aktenzeichen
2. Sachverhaltsschilderung
3. Rechtliche Bewertung
4. Schadensaufstellung detailliert
5. Anspruchsgrundlagen
6. Fristsetzung zur Regulierung
7. Androhung rechtlicher Schritte
8. Beweismittel-Hinweise"""
        },

        DocumentType.VERTRAG: {
            "system": BASE_SYSTEM_PROMPT + """

SPEZIALISIERUNG: Vertragsgestaltung
- Alle wesentlichen Vertragsbestandteile definieren
- AGB-Kontrolle nach §§ 305 ff. BGB berücksichtigen
- Kündigung und Laufzeit regeln
- Salvatorische Klausel einfügen
- Gerichtsstand und anwendbares Recht""",
            
            "structure": """
AUFBAU VERTRAG:
1. Vertragsparteien vollständig
2. Präambel/Vertragsgegenstand
3. Leistungspflichten beider Seiten
4. Vergütung und Zahlungsmodalitäten
5. Laufzeit und Kündigung
6. Haftung und Gewährleistung
7. Datenschutz
8. Schlussbestimmungen
9. Unterschriften beider Parteien"""
        },

        DocumentType.KUENDIGUNG: {
            "system": BASE_SYSTEM_PROMPT + """

SPEZIALISIERUNG: Kündigungsschreiben
- Kündigungsfristen nach BGB/Arbeitsrecht beachten
- Unterscheidung ordentliche/außerordentliche Kündigung
- Begründung bei fristloser Kündigung erforderlich
- Sozialauswahl bei betriebsbedingter Kündigung
- Übergabepflichten regeln""",
            
            "structure": """
AUFBAU KÜNDIGUNG:
1. Eindeutige Kündigungserklärung
2. Kündigungsgrund (bei außerordentlicher)
3. Kündigungstermin exakt benennen
4. Freistellung oder Weiterbeschäftigung
5. Rückgabe von Arbeitsmitteln
6. Zeugnis-Anspruch erwähnen
7. Rechtsmittelbelehrung"""
        },

        DocumentType.GEHEIMHALTUNG: {
            "system": BASE_SYSTEM_PROMPT + """

SPEZIALISIERUNG: Geheimhaltungsvereinbarungen (NDAs)
- Präzise Definition vertraulicher Informationen
- Ausnahmen von der Geheimhaltung definieren
- Dauer der Geheimhaltungspflicht festlegen
- Vertragsstrafe bei Verstoß
- Rückgabe von Unterlagen regeln""",
            
            "structure": """
AUFBAU GEHEIMHALTUNGSVEREINBARUNG:
1. Vertragsparteien und Zweck
2. Definition vertraulicher Informationen
3. Geheimhaltungspflichten
4. Ausnahmen und Grenzen
5. Dauer der Geheimhaltung
6. Rückgabe von Unterlagen
7. Vertragsstrafe
8. Anwendbares Recht"""
        }
    }

    CONTEXT_ENHANCERS = {
        "legal_authority": "Als spezialisierte Anwaltskanzlei mit Expertise in {area}",
        "urgency": "Aufgrund der Dringlichkeit der Angelegenheit",
        "client_protection": "Im Interesse unseres Mandanten",
        "legal_compliance": "Unter Beachtung der aktuellen Rechtsprechung",
        "professional_standard": "Nach den Standards der Rechtsanwaltskammer"
    }

    @classmethod
    def get_system_prompt(cls, document_type: DocumentType = DocumentType.ALLGEMEIN, 
                         context: Dict[str, Any] = None) -> str:
        """
        Generate context-aware system prompt for German legal documents
        
        Args:
            document_type: Type of legal document to generate
            context: Additional context information
            
        Returns:
            Optimized system prompt for Together.ai
        """
        if context is None:
            context = {}
            
        # Get base prompt for document type
        if document_type in cls.DOCUMENT_SPECIFIC_PROMPTS:
            base_prompt = cls.DOCUMENT_SPECIFIC_PROMPTS[document_type]["system"]
        else:
            base_prompt = cls.BASE_SYSTEM_PROMPT
        
        # Add context-specific enhancements
        enhancements = []
        
        if context.get("urgent", False):
            enhancements.append("DRINGEND: Diese Angelegenheit erfordert sofortige Aufmerksamkeit.")
            
        if context.get("template_used"):
            enhancements.append(f"Verwende die bereitgestellte Vorlage als Grundlage.")
            
        if context.get("legal_area"):
            area = context["legal_area"]
            enhancements.append(f"Spezialisierung auf {area} berücksichtigen.")
            
        if context.get("amount"):
            amount = context["amount"]
            enhancements.append(f"Streitwert: {amount} EUR - angemessene Kosten berücksichtigen.")
        
        # Combine base prompt with enhancements
        if enhancements:
            enhanced_prompt = base_prompt + "\n\nKONTEXT-SPEZIFISCHE ANFORDERUNGEN:\n" + "\n".join(f"- {e}" for e in enhancements)
        else:
            enhanced_prompt = base_prompt
            
        return enhanced_prompt

    @classmethod
    def get_user_prompt(cls, user_input: str, document_type: DocumentType = DocumentType.ALLGEMEIN,
                       template_content: str = None) -> str:
        """
        Generate user prompt for document generation
        
        Args:
            user_input: User's document request
            document_type: Type of document
            template_content: Optional template to use as base
            
        Returns:
            Formatted user prompt
        """
        prompts = []
        
        if template_content:
            prompts.append(f"VORLAGE ALS GRUNDLAGE:\n{template_content}\n")
            prompts.append(f"ANPASSUNG ERFORDERLICH:\n{user_input}")
        else:
            prompts.append(f"DOKUMENTANFRAGE:\n{user_input}")
        
        # Add document type specific instructions
        if document_type in cls.DOCUMENT_SPECIFIC_PROMPTS:
            structure = cls.DOCUMENT_SPECIFIC_PROMPTS[document_type].get("structure", "")
            if structure:
                prompts.append(f"\nERWARTETE STRUKTUR:\n{structure}")
        
        prompts.append("\nErstelle ein vollständiges, sofort verwendbares deutsches Rechtsdokument.")
        
        return "\n".join(prompts)

    @classmethod
    def get_response_generation_prompt(cls, sanitized_email: str, context: str = "") -> str:
        """
        Generate prompt for AI email response generation
        
        Args:
            sanitized_email: PII-sanitized email content
            context: Additional context for response
            
        Returns:
            Prompt for generating professional German legal response
        """
        system_prompt = """Du bist ein erfahrener deutscher Rechtsanwalt. 
        
Erstelle eine professionelle, höfliche Antwort auf die folgende E-Mail in deutscher Sprache.

ANFORDERUNGEN:
- Professionelle, juristische Sprache
- Höfliche und respektvolle Anrede
- Sachliche Behandlung des Anliegens
- Konkrete nächste Schritte vorschlagen
- Kontaktdaten der Kanzlei einbeziehen
- Rechtliche Hinweise wo angebracht
- Formelle Schlussformel

ANTWORT-STRUKTUR:
1. Höfliche Anrede
2. Bezug auf das Anliegen
3. Rechtliche Einschätzung/Beratung
4. Nächste Schritte
5. Terminvorschlag für Beratung
6. Höfliche Schlussformel"""

        user_prompt = f"""E-MAIL-INHALT (anonymisiert):
{sanitized_email}

ZUSÄTZLICHER KONTEXT:
{context}

Erstelle eine vollständige, professionelle E-Mail-Antwort auf Deutsch."""

        return system_prompt, user_prompt

# Pre-configured model parameters for Together.ai
TOGETHER_AI_CONFIG = {
    "model": "moonshotai/Kimi-K2-Instruct",  # High-quality multilingual support including German
    "max_tokens": 4096,
    "temperature": 0.1,  # Low temperature for legal precision
    "top_p": 0.9,
    "repetition_penalty": 1.1,
    "stop": ["###", "[END]", "<|eot_id|>"]
}

# Alternative models for different use cases
MODEL_CONFIGS = {
    "precise": {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "temperature": 0.05,
        "top_p": 0.85
    },
    "creative": {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", 
        "temperature": 0.3,
        "top_p": 0.95
    },
    "fast": {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "temperature": 0.1,
        "top_p": 0.9
    }
}