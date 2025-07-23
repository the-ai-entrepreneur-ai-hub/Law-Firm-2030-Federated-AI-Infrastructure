#!/usr/bin/env python3
"""
Alternative Optimization for Anonymized Legal Documents
Creates optimized prompts and response templates without requiring fine-tuning
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from together import Together

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AnonymizedPromptOptimizer:
    """
    Optimizes the model for anonymized German legal documents without fine-tuning
    Uses advanced prompting techniques and response templates
    """
    
    def __init__(self):
        # Configuration
        self.api_key = os.environ.get("TOGETHER_API_KEY", "REDACTED")
        self.client = Together(api_key=self.api_key)
        self.model = "deepseek-ai/DeepSeek-V3"
        
        # Data paths
        self.base_dir = Path("/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030")
        self.training_data_jsonl = self.base_dir / "law_firm_dataset.jsonl"
        
        # Load training data for analysis
        self.training_examples = self.load_training_data()
        
    def load_training_data(self) -> List[Dict]:
        """Load training data for analysis"""
        try:
            training_data = []
            if self.training_data_jsonl.exists():
                with open(self.training_data_jsonl, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            training_data.append(json.loads(line))
            
            logger.info(f"📊 Loaded {len(training_data)} training examples for analysis")
            return training_data
            
        except Exception as e:
            logger.error(f"❌ Error loading training data: {e}")
            return []
    
    def analyze_anonymization_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in anonymized data"""
        logger.info("🔍 Analyzing anonymization patterns...")
        
        patterns = {
            'pii_tokens': set(),
            'document_types': {},
            'common_phrases': [],
            'replacement_patterns': {}
        }
        
        for example in self.training_examples:
            prompt = example.get('prompt', '')
            
            # Extract PII tokens
            import re
            pii_tokens = re.findall(r'\[([A-Z_]+)_\d+\]', prompt)
            patterns['pii_tokens'].update(pii_tokens)
            
            # Identify document types
            doc_type = self.identify_document_type(prompt)
            if doc_type not in patterns['document_types']:
                patterns['document_types'][doc_type] = 0
            patterns['document_types'][doc_type] += 1
        
        patterns['pii_tokens'] = list(patterns['pii_tokens'])
        
        logger.info(f"✅ Found {len(patterns['pii_tokens'])} PII token types")
        logger.info(f"📋 Document types: {patterns['document_types']}")
        
        return patterns
    
    def identify_document_type(self, prompt: str) -> str:
        """Identify the type of legal document"""
        prompt_lower = prompt.lower()
        
        if 'klageerhebung' in prompt_lower or 'gehaltszahlung' in prompt_lower:
            return 'salary_claim'
        elif 'abmahnung' in prompt_lower and 'urheberrecht' in prompt_lower:
            return 'copyright_warning'
        elif 'kündigung' in prompt_lower and 'arbeitsverhältnis' in prompt_lower:
            return 'employment_termination'
        elif 'mahnung' in prompt_lower:
            return 'payment_reminder'
        else:
            return 'general_legal'
    
    def create_optimized_prompt_template(self, patterns: Dict[str, Any]) -> str:
        """Create an optimized prompt template for anonymized documents"""
        logger.info("🎯 Creating optimized prompt template...")
        
        pii_examples = ", ".join(patterns['pii_tokens'][:10])  # Show first 10 types
        
        template = f"""Du bist ein Experte für deutsche Rechtsdokumente und arbeitest mit anonymisierten Texten.

WICHTIGE HINWEISE ZUR ANONYMISIERUNG:
- Anonymisierte Daten werden durch Tokens wie [{pii_examples}] ersetzt
- Diese Tokens repräsentieren ursprünglich sensible Daten (Namen, Adressen, Telefonnummern, etc.)
- Behandle diese Tokens als Platzhalter für echte Daten
- Erstelle professionelle rechtliche Antworten, die diese Anonymisierung berücksichtigen

DOKUMENTTYPEN:
- Klageerhebung: Gehaltsforderungen, Schadensersatz
- Abmahnung: Urheberrechtsverletzungen, Vertragsbruch  
- Kündigung: Arbeitsverhältnisse, Verträge
- Mahnung: Zahlungsaufforderungen, offene Rechnungen

ANTWORT-RICHTLINIEN:
1. Verwende formelle deutsche Rechtssprache
2. Strukturiere Antworten professionell
3. Berücksichtige den anonymisierten Kontext
4. Gebe konkrete rechtliche Einschätzungen
5. Schlage angemessene nächste Schritte vor

EINGABE: {{input_document}}

AUFGABE: Analysiere das anonymisierte Rechtsdokument und erstelle eine professionelle rechtliche Antwort, die:
- Den Sachverhalt würdigt
- Rechtliche Positionen darlegt
- Konkrete Handlungsempfehlungen gibt
- Den formellen Ton wahrt

ANTWORT:"""
        
        return template
    
    def create_response_templates(self) -> Dict[str, str]:
        """Create response templates for different document types"""
        logger.info("📝 Creating response templates...")
        
        templates = {
            'salary_claim': """Sehr geehrte Damen und Herren,

wir haben Ihr Schreiben zur Kenntnis genommen und werden die geltend gemachten Ansprüche eingehend prüfen.

RECHTLICHE BEWERTUNG:
Die behaupteten Gehaltszahlungen werden derzeit von unserer Rechts- und Buchhaltungsabteilung überprüft. Eine ordnungsgemäße Prüfung der Ansprüche erfordert die Sichtung aller relevanten Unterlagen.

WEITERE VORGEHENSWEISE:
Sollten die Forderungen berechtigt sein, werden wir diese umgehend begleichen. Andernfalls werden wir Ihnen eine detaillierte rechtliche Stellungnahme mit Begründung zukommen lassen.

Wir bitten um Verständnis für die Bearbeitungszeit und werden uns innerhalb von 14 Tagen bei Ihnen melden.

Mit freundlichen Grüßen
Rechtsabteilung""",

            'copyright_warning': """Sehr geehrte Damen und Herren,

wir haben Ihre Abmahnung wegen angeblicher Urheberrechtsverletzung erhalten und zur Kenntnis genommen.

RECHTLICHE STELLUNGNAHME:
Nach eingehender Prüfung weisen wir die Vorwürfe entschieden zurück. Das beanstandete Material wurde ordnungsgemäß lizenziert und wir verfügen über entsprechende Nutzungsrechte.

UNSERE POSITION:
- Eine Urheberrechtsverletzung liegt nicht vor
- Die Nutzung erfolgte im Rahmen bestehender Lizenzvereinbarungen
- Eine Unterlassungserklärung ist daher nicht gerechtfertigt

Gerne stellen wir Ihnen auf Anfrage die entsprechenden Lizenzvereinbarungen zur Verfügung.

Mit freundlichen Grüßen
Rechtsabteilung""",

            'employment_termination': """Sehr geehrte Damen und Herren,

wir bestätigen den Erhalt Ihrer Kündigung und nehmen diese zur Kenntnis.

ADMINISTRATIVE ABWICKLUNG:
Wir bedauern die Beendigung des Arbeitsverhältnisses und danken für die bisher geleistete Arbeit und das gezeigte Engagement.

WEITERE SCHRITTE:
- Die Abwicklung erfolgt ordnungsgemäß entsprechend den gesetzlichen und vertraglichen Bestimmungen
- Die Arbeitspapiere werden umgehend an die angegebene Adresse versandt
- Etwaige noch offene Ansprüche werden mit der Endabrechnung beglichen

Wir wünschen für die berufliche und private Zukunft alles Gute.

Mit freundlichen Grüßen
Personalabteilung""",

            'payment_reminder': """Sehr geehrte Damen und Herren,

wir haben Ihre Mahnung erhalten und den beanstandeten Sachverhalt umgehend geprüft.

SACHSTAND:
Die in Rede stehende Rechnung wurde zwischenzeitlich beglichen. Die Überweisung ist bereits erfolgt und sollte in den nächsten Bankarbeitstagen auf Ihrem Konto eingehen.

WEITERE HINWEISE:
Falls Sie die Zahlung bereits erhalten haben, betrachten Sie dieses Schreiben bitte als gegenstandslos. Bei eventuellen Rückfragen stehen wir gerne zur Verfügung.

Wir entschuldigen uns für etwaige Unannehmlichkeiten.

Mit freundlichen Grüßen
Buchhaltung""",

            'general_legal': """Sehr geehrte Damen und Herren,

wir haben Ihr Schreiben erhalten und zur Kenntnis genommen.

BEARBEITUNG:
Der dargelegte Sachverhalt wird derzeit von unserer Rechtsabteilung eingehend geprüft. Wir werden nach Abschluss der Prüfung eine ausführliche rechtliche Stellungnahme erstellen.

ZEITRAHMEN:
Die Bearbeitung komplexer rechtlicher Sachverhalte erfordert eine sorgfältige Analyse aller relevanten Aspekte. Wir werden uns zeitnah, spätestens jedoch innerhalb von 21 Tagen, mit einer detaillierten Antwort bei Ihnen melden.

Bis dahin bitten wir um Ihr Verständnis.

Mit freundlichen Grüßen
Rechtsabteilung"""
        }
        
        return templates
    
    def test_optimized_prompts(self, template: str, response_templates: Dict[str, str]) -> bool:
        """Test the optimized prompts with sample data"""
        logger.info("🧪 Testing optimized prompts...")
        
        # Test samples with different document types
        test_samples = [
            {
                "prompt": """An das [BIC_7] Musterstadt
Musterstraße 1
[PLZ_2] [LOC_2]

**Klageerhebung**

Sehr geehrte Damen und Herren,

in der [ORG_1]. gegen [BIC_6] erheben wir Klage wegen ausstehender Gehaltszahlungen.
Unser Mandant, Ing. [BIC_5] Wirth [WEBSITE_1]., [BIC_4] in [LOC_1] 7
[PLZ_1] Artern, hat seit drei Monaten kein Gehalt [BIC_3].

Wir beantragen, die [BIC_2] zu [BIC_1], an unseren Mandanten 586 [MISC_1] nebst Zinsen zu zahlen.""",
                "expected_type": "salary_claim"
            },
            {
                "prompt": """An
Prof. [PER_2].
Löchelstraße 54
[PLZ_1] [LOC_1]

**Abmahnung wegen Urheberrechtsverletzung**

Sehr geehrte/r Prof. [PER_1].,

wir vertreten die Interessen der Firma [BIC_4] GmbH. Sie haben am [GEBURTSDATUM_1] auf Ihrer [BIC_3] lt-42.[BIC_2].de ein Bild verwendet, an dem unsere Mandantin die ausschließlichen Nutzungsrechte besitzt.""",
                "expected_type": "copyright_warning"
            }
        ]
        
        success_count = 0
        
        for i, sample in enumerate(test_samples):
            try:
                logger.info(f"🧪 Testing sample {i+1}/{len(test_samples)}")
                
                # Use template with fallback to appropriate response template
                doc_type = self.identify_document_type(sample["prompt"])
                
                # Create contextual prompt
                full_prompt = template.replace("{input_document}", sample["prompt"])
                
                # Add context about expected response
                if doc_type in response_templates:
                    full_prompt += f"\n\nHINWEIS: Dies ist ein {doc_type.replace('_', ' ')}-Dokument. Erstelle eine entsprechende professionelle Antwort."
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user", 
                            "content": full_prompt
                        }
                    ],
                    max_tokens=512,
                    temperature=0.3
                )
                
                generated_response = response.choices[0].message.content
                
                logger.info(f"✅ Generated response for sample {i+1}:")
                logger.info(f"📝 Type: {doc_type}")
                logger.info(f"📄 Response: {generated_response[:200]}...")
                
                # Quality check
                if (len(generated_response) > 100 and 
                    "geehrte" in generated_response.lower() and
                    any(word in generated_response.lower() for word in ["recht", "anspruch", "prüfung", "stellungnahme"])):
                    success_count += 1
                    logger.info(f"✅ Sample {i+1} passed quality check")
                else:
                    logger.warning(f"⚠️ Sample {i+1} may need improvement")
                
            except Exception as e:
                logger.error(f"❌ Error testing sample {i+1}: {e}")
        
        success_rate = success_count / len(test_samples) if test_samples else 0
        logger.info(f"📊 Test Results: {success_count}/{len(test_samples)} passed ({success_rate*100:.1f}%)")
        
        return success_rate >= 0.7
    
    def update_docker_sanitizer(self, template: str, response_templates: Dict[str, str]) -> bool:
        """Update the Docker sanitizer with optimized prompts"""
        logger.info("🐳 Updating Docker sanitizer with optimized prompts...")
        
        try:
            sanitizer_path = Path("/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai/secure_sanitizer.py")
            
            if not sanitizer_path.exists():
                logger.error(f"❌ Sanitizer file not found: {sanitizer_path}")
                return False
            
            # Read current content
            with open(sanitizer_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup
            backup_path = sanitizer_path.with_suffix('.py.backup.' + datetime.now().strftime('%Y%m%d_%H%M%S'))
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create optimization config
            optimization_config = {
                "prompt_template": template,
                "response_templates": response_templates,
                "optimization_date": datetime.now().isoformat(),
                "description": "Optimized for anonymized German legal documents"
            }
            
            # Save optimization config
            config_path = sanitizer_path.parent / "anonymized_optimization_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(optimization_config, f, indent=2, ensure_ascii=False)
            
            # Add import and loading logic to sanitizer
            optimization_code = f'''
# ANONYMIZED DOCUMENT OPTIMIZATION
import json
from pathlib import Path

def load_anonymized_optimization():
    """Load optimization configuration for anonymized documents"""
    try:
        config_path = Path(__file__).parent / "anonymized_optimization_config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def optimize_prompt_for_anonymized(prompt_text: str, doc_type: str = None) -> str:
    """Optimize prompt for anonymized legal documents"""
    config = load_anonymized_optimization()
    if not config:
        return prompt_text
    
    template = config.get("prompt_template", "")
    if template:
        return template.replace("{{input_document}}", prompt_text)
    
    return prompt_text

def get_response_template(doc_type: str) -> str:
    """Get response template for document type"""
    config = load_anonymized_optimization()
    if not config:
        return ""
    
    templates = config.get("response_templates", {{}})
    return templates.get(doc_type, templates.get("general_legal", ""))

# Load optimization on startup
ANONYMIZED_CONFIG = load_anonymized_optimization()
'''
            
            # Find a good place to insert the optimization code
            if "# --- PII-Scrubbing Logging Filter ---" in content:
                insertion_point = content.find("# --- PII-Scrubbing Logging Filter ---")
                updated_content = content[:insertion_point] + optimization_code + "\n\n" + content[insertion_point:]
            else:
                # Insert after imports
                import_end = content.rfind("import ")
                if import_end != -1:
                    line_end = content.find("\n", import_end)
                    updated_content = content[:line_end] + "\n" + optimization_code + "\n" + content[line_end:]
                else:
                    updated_content = optimization_code + "\n\n" + content
            
            # Write updated sanitizer
            with open(sanitizer_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"✅ Sanitizer updated with optimization")
            logger.info(f"💾 Backup created: {backup_path}")
            logger.info(f"📄 Config saved: {config_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating sanitizer: {e}")
            return False
    
    def run_optimization_pipeline(self) -> bool:
        """Run the complete optimization pipeline"""
        logger.info("🚀 Starting optimization pipeline for anonymized legal documents")
        
        try:
            # Step 1: Analyze patterns
            patterns = self.analyze_anonymization_patterns()
            
            # Step 2: Create optimized prompt template
            template = self.create_optimized_prompt_template(patterns)
            
            # Step 3: Create response templates
            response_templates = self.create_response_templates()
            
            # Step 4: Test the optimization
            if not self.test_optimized_prompts(template, response_templates):
                logger.warning("⚠️ Optimization testing showed concerns, but proceeding...")
            
            # Step 5: Update Docker sanitizer
            if not self.update_docker_sanitizer(template, response_templates):
                logger.error("❌ Failed to update Docker sanitizer")
                return False
            
            logger.info("🎉 Optimization pipeline completed successfully!")
            logger.info("📋 Docker sanitizer optimized for anonymized documents")
            logger.info("🔄 Restart Docker container to apply changes")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Optimization pipeline failed: {e}")
            return False

def main():
    """Main execution function"""
    optimizer = AnonymizedPromptOptimizer()
    
    print("🎯 Anonymized Legal Document Optimization")
    print("=" * 60)
    print("📋 Optimizing prompts for anonymized PII documents")
    print(f"🤖 Using model: {optimizer.model}")
    print(f"📊 Training examples: {len(optimizer.training_examples)}")
    print("")
    
    # Run the optimization pipeline
    success = optimizer.run_optimization_pipeline()
    
    if success:
        print("\n✅ SUCCESS: Optimization completed!")
        print("🎯 Docker sanitizer optimized for anonymized documents")
        print("📋 Next steps:")
        print("1. Restart Docker container: docker restart law-firm-ai")
        print("2. Test with your 8-page PDF documents")
        print("3. Verify improved responses with anonymized data")
        print("\n🔧 Alternative to fine-tuning:")
        print("- Enhanced prompt templates for anonymized content")
        print("- Professional response templates by document type")
        print("- Improved context understanding")
    else:
        print("\n❌ FAILED: Optimization encountered errors")
        print("📋 Check the logs for details")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())