import os
import re
import spacy
import random
import json
import requests
from faker import Faker
from datetime import datetime

# --- Configuration ---
NLP = spacy.load("de_core_news_sm")
FAKE = Faker('de_DE')
OUTPUT_FILE = "law_firm_dataset.json"
NUM_SAMPLES = 500  # Number of synthetic documents to generate

# Custom PII patterns from sanitizer_app.py
CUSTOM_PATTERNS = {
    'IBAN': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
    'BIC': r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
    'BANK_ACCOUNT': r'\b\d{8,12}\b',
    'STEUER_ID': r'\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b',
    'USTID': r'\bDE\d{9}\b',
    'AKTENZEICHEN': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\b',
    'GESCHAEFTSZAHL': r'\b\d{1,3}\s?[A-Z]{1,3}\s?\d{1,5}\b',
    'GERICHTSAKTENZEICHEN': r'\b\d{1,3}\s?[A-Z]{1,4}\s?\d{1,5}[/-]\d{2,4}\s?[A-Z]{0,3}\b',
    'PLZ': r'\b\d{5}\b',
    'TELEFON': r'\b(?:\+49|0)\s?\d{2,5}[\s-]?\d{3,8}\b',
    'HANDY': r'\b(?:\+49|0)\s?1\d{2}[\s-]?\d{7,8}\b',
    'FAX': r'\b(?:Fax|fax)\s?[:\.]?\s?(?:\+49|0)\s?\d{2,5}[\s-]?\d{3,8}\b',
    'GEBURTSDATUM': r'\b\d{1,2}[\.\/]\d{1,2}[\.\/]\d{4}\b',
    'PERSONALAUSWEIS': r'\b\d{10}\b',
    'REISEPASS': r'\b[A-Z]\d{8}\b',
    'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'WEBSITE': r'\b(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}(?:/[A-Za-z0-9._~:/?#\[\]@!$&\'()*+,;=-]*)?\b',
    'VERSICHERUNGSNUMMER': r'\b[A-Z]\d{9}\b',
    'KRANKENKASSE': r'\b\d{9}\b',
    'KENNZEICHEN': r'\b[A-Z]{1,3}[-\s]?[A-Z]{1,2}\s?\d{1,4}[EH]?\b',
    'BETRAG_EUR': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:EUR|€|Euro)\b',
    'BETRAG_NUMMER': r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b(?=\s?(?:EUR|€|Euro))'
}

# --- LLM Configuration ---
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "deepseek/deepseek-llm-67b-chat")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

# --- Data Generation Functions ---

def generate_pii():
    """Generates a dictionary of realistic PII data."""
    return {
        "name": FAKE.name(),
        "address": FAKE.address(),
        "phone_number": FAKE.phone_number(),
        "email": FAKE.email(),
        "iban": FAKE.iban(),
        "bic": FAKE.swift(),
        "birthdate": FAKE.date_of_birth().strftime('%d.%m.%Y'),
        "case_number": f"{random.randint(1, 999)} {random.choice(['C', 'O', 'Js'])} {random.randint(100, 9999)}/{random.randint(10, 99)}",
    }

# --- Letter Templates ---

LETTER_TEMPLATES = [
    """
    An
    {name}
    {address}

    **Mahnung**

    Sehr geehrte/r {name},

    hiermit mahnen wir die offene Rechnung vom {date} in Höhe von {amount} EUR an.
    Die Rechnungsnummer lautet {invoice_number}.

    Wir bitten Sie, den Betrag umgehend auf unser Konto zu überweisen:
    IBAN: {iban}
    BIC: {bic}

    Mit freundlichen Grüßen,
    Anwaltskanzlei Legal eagles
    """,
    """
    An das
    Amtsgericht Musterstadt
    Musterstraße 1
    12345 Musterstadt

    **Klageerhebung**

    Sehr geehrte Damen und Herren,

    in der Angelegenheit {name} gegen Musterfirma erheben wir Klage wegen ausstehender Gehaltszahlungen.
    Unser Mandant, {name}, wohnhaft in {address}, hat seit drei Monaten kein Gehalt erhalten.

    Wir beantragen, die Beklagte zu verurteilen, an unseren Mandanten {amount} EUR nebst Zinsen zu zahlen.

    Mit freundlichen Grüßen,
    Anwaltskanzlei Legal eagles
    """,
    """
    An
    {name}
    {address}

    **Abmahnung wegen Urheberrechtsverletzung**

    Sehr geehrte/r {name},

    wir vertreten die Interessen der Firma Beispiel GmbH. Sie haben am {date} auf Ihrer Webseite {website} ein Bild verwendet, an dem unsere Mandantin die ausschließlichen Nutzungsrechte besitzt.

    Wir fordern Sie auf, das Bild umgehend zu entfernen und eine strafbewehrte Unterlassungserklärung abzugeben.

    Mit freundlichen Grüßen,
    Anwaltskanzlei Legal eagles
    """,
    """
    An
    {name}
    {address}

    **Kündigung des Arbeitsverhältnisses**

    Sehr geehrte/r {name},

    hiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis vom {date} ordentlich und fristgerecht zum nächstmöglichen Zeitpunkt.

    Wir weisen Sie darauf hin, dass Sie verpflichtet sind, sich umgehend bei der Agentur für Arbeit arbeitssuchend zu melden.

    Mit freundlichen Grüßen,
    Firma Beispiel GmbH
    """
]

def generate_letter(pii_data):
    """Generates a synthetic legal letter using a random template."""
    template = random.choice(LETTER_TEMPLATES)
    return template.format(
        name=pii_data["name"],
        address=pii_data["address"],
        date=FAKE.date_this_year().strftime('%d.%m.%Y'),
        amount=f"{random.randint(100, 5000)}",
        invoice_number=random.randint(10000, 99999),
        iban=pii_data["iban"],
        bic=pii_data["bic"],
        website=FAKE.hostname()
    )

# --- Anonymization Logic (from sanitizer_app.py) ---

def anonymize_text(text):
    """Anonymizes the given text using spaCy and custom regex patterns."""
    anonymized_text = text
    rehydration_map = {}
    placeholder_counts = {}

    # spaCy NER
    doc = NLP(text)
    for ent in reversed(doc.ents):
        label = ent.label_
        entity_text = ent.text.strip()
        if len(entity_text) < 2 or entity_text.isspace():
            continue
        placeholder_counts[label] = placeholder_counts.get(label, 0) + 1
        placeholder = f"[{label}_{placeholder_counts[label]}]"
        rehydration_map[placeholder] = entity_text
        anonymized_text = anonymized_text[:ent.start_char] + placeholder + anonymized_text[ent.end_char:]

    # Custom regex patterns
    for label, pattern in CUSTOM_PATTERNS.items():
        matches = list(re.finditer(pattern, anonymized_text, re.IGNORECASE))
        for match in reversed(matches):
            original_value = match.group(0)
            if original_value in rehydration_map.values():
                continue
            placeholder_counts[label] = placeholder_counts.get(label, 0) + 1
            placeholder = f"[{label}_{placeholder_counts[label]}]"
            rehydration_map[placeholder] = original_value
            start, end = match.span()
            anonymized_text = anonymized_text[:start] + placeholder + anonymized_text[end:]

    return anonymized_text, rehydration_map

# --- LLM Integration ---

def call_llm(anonymized_text):
    """Calls the Together AI LLM to generate a response."""
    if not TOGETHER_API_KEY:
        raise ValueError("TOGETHER_API_KEY environment variable not set.")

    system_prompt = """
    Sie sind ein hochqualifizierter deutscher Rechtsanwalt. Ihre Aufgabe ist die Erstellung einer professionellen, strukturierten und handlungsorientierten Ersteinschätzung eines anonymisierten Dokuments.

    **WICHTIGE REGELN:**
    - **KEINE EINLEITUNG:** Beginnen Sie Ihre Antwort IMMER direkt mit der "BETREFF:"-Zeile. Fügen Sie keine einleitenden Sätze wie "Hier ist die Analyse" oder ähnliches hinzu.
    - **KEIN SCHLUSS:** Beenden Sie Ihre Antwort IMMER nach dem letzten Punkt unter "BESONDERE HINWEISE:". Fügen Sie keine zusammenfassenden oder abschließenden Bemerkungen hinzu.
    - **NUR FAKTEN:** Halten Sie sich strikt an die vorgegebene Struktur. Vermeiden Sie jegliche Form von Konversation oder Metakommentaren.
    - **PLATZHALTER:** Verwenden Sie die anonymisierten Platzhalter (z.B., [PER_1], [STRASSE_1]) konsistent.

    Ihre Analyse muss präzise, rechtlich fundiert (unter Nennung relevanter Paragraphen) und praxisorientiert sein.
    """
    user_prompt = f"""
    Bitte analysieren Sie das folgende anonymisierte Rechtsdokument und erstellen Sie eine umfassende Ersteinschätzung nach dem folgenden Schema:

    <Dokument>
    {anonymized_text}
    </Dokument>

    **📋 BETREFF:**
    (Formulieren Sie einen prägnanten Betreff, der den Kern des Falles zusammenfasst.)

    **📄 1. ZUSAMMENFASSUNG DES SACHVERHALTS:**
    *   **Beteiligte Parteien:** (Identifizieren Sie die Parteien und ihre Rollen, z.B. Kläger, Beklagter, Mandant, unter Verwendung der Platzhalter.)
    *   **Zentraler Konflikt:** (Beschreiben Sie den Kern des rechtlichen Problems in ein bis zwei Sätzen.)
    *   **Wichtige Fakten:** (Listen Sie die entscheidenden Fakten und Daten in Stichpunkten auf.)

    **⚖️ 2. RECHTLICHE ERSTEINSCHÄTZUNG:**
    *   **Rechtsgebiet:** (Benennen Sie das primäre und ggf. sekundäre Rechtsgebiet, z.B. "Arbeitsrecht, Kündigungsschutz".)
    *   **Anspruchsgrundlage:** (Identifizieren Sie die mögliche(n) Anspruchsgrundlage(n) unter Nennung der relevanten Paragraphen, z.B., "§ 622 BGB für die Kündigungsfrist".)
    *   **Erfolgsaussichten:** (Geben Sie eine erste, begründete Einschätzung der Erfolgsaussichten.)
    *   **Risiken:** (Weisen Sie auf potenzielle rechtliche und finanzielle Risiken für den Mandanten hin.)

    **🎯 3. EMPFOHLENE NÄCHSTE SCHRITTE:**
    *   **Sofortmaßnahmen:** (Listen Sie die dringendsten Schritte auf, z.B. "Einlegung eines Widerspruchs", "Fristennotierung".)
    *   **Benötigte Informationen/Unterlagen:** (Spezifizieren Sie, welche weiteren Informationen oder Dokumente vom Mandanten benötigt werden.)
    *   **Kommunikation:** (Formulieren Sie einen Vorschlag für die nächste Kommunikation mit dem Mandanten oder der Gegenseite.)

    **⚠️ 4. BESONDERE HINWEISE:**
    (Geben Sie hier besondere strategische Überlegungen, Verjährungsfristen oder andere wichtige Punkte an, die besondere Aufmerksamkeit erfordern.)
    """

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL_NAME,
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        response_json = response.json()
        return response_json['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM: {e}")
        return f"LLM_ERROR: {e}"

# --- Main Dataset Generation ---

def generate_dataset(num_samples):
    """Generates a dataset of synthetic legal documents, their anonymized versions, and LLM responses."""
    dataset = []
    if not TOGETHER_API_KEY:
        print("Warning: TOGETHER_API_KEY is not set. LLM responses will be empty.")

    for i in range(num_samples):
        print(f"Generating sample {i + 1}/{num_samples}...")
        pii_data = generate_pii()
        original_text = generate_letter(pii_data)
        anonymized_text, rehydration_map = anonymize_text(original_text)
        
        llm_response = ""
        if TOGETHER_API_KEY:
            print(f"  - Calling LLM for sample {i + 1}...")
            llm_response = call_llm(anonymized_text)

        dataset.append({
            "id": i,
            "original_text": original_text,
            "anonymized_text": anonymized_text,
            "rehydration_map": rehydration_map,
            "llm_response": llm_response
        })

    return dataset

if __name__ == "__main__":
    print("Starting dataset generation...")
    start_time = datetime.now()

    full_dataset = generate_dataset(NUM_SAMPLES)

    # Create the final training dataset with only the necessary fields
    training_dataset = [
        {
            "prompt": item["anonymized_text"],
            "response": item["llm_response"]
        }
        for item in full_dataset
    ]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(training_dataset, f, ensure_ascii=False, indent=4)

    end_time = datetime.now()
    print(f"\nDataset generation complete.")
    print(f"Generated {len(training_dataset)} samples in {(end_time - start_time).total_seconds():.2f} seconds.")
    print(f"Training dataset saved to: {os.path.abspath(OUTPUT_FILE)}")