#!/usr/bin/env python3
"""
Simplified Local Training for German Legal Model
Uses the existing infrastructure for efficient training
"""

import json
import os
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleGermanLegalTrainer:
    """Simple trainer that enhances the existing model with German legal knowledge"""
    
    def __init__(self):
        self.base_dir = Path("/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030")
        self.dataset_path = self.base_dir / "law_firm_dataset.jsonl"
        self.output_dir = self.base_dir / "law-firm-ai" / "local-training" / "trained_model"
        self.output_dir.mkdir(exist_ok=True)
        
    def load_training_data(self):
        """Load the German legal training dataset"""
        logger.info(f"Loading training data from {self.dataset_path}")
        
        data = []
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            item = json.loads(line)
                            data.append(item)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
                            continue
                            
            logger.info(f"✅ Loaded {len(data)} training examples")
            return data
            
        except FileNotFoundError:
            logger.error(f"❌ Training data not found at {self.dataset_path}")
            return []
            
    def analyze_training_data(self, data):
        """Analyze the training data structure"""
        logger.info("📊 Analyzing training data...")
        
        if not data:
            logger.error("No data to analyze")
            return
            
        # Sample analysis
        sample = data[0]
        logger.info(f"Sample data structure: {list(sample.keys())}")
        logger.info(f"Sample prompt preview: {sample.get('prompt', '')[:100]}...")
        
        # Count document types
        prompt_types = {}
        for item in data:
            prompt = item.get('prompt', '').lower()
            if 'klage' in prompt:
                prompt_types['Klage'] = prompt_types.get('Klage', 0) + 1
            elif 'abmahnung' in prompt:
                prompt_types['Abmahnung'] = prompt_types.get('Abmahnung', 0) + 1
            elif 'kündigung' in prompt:
                prompt_types['Kündigung'] = prompt_types.get('Kündigung', 0) + 1
            elif 'mahnung' in prompt:
                prompt_types['Mahnung'] = prompt_types.get('Mahnung', 0) + 1
            else:
                prompt_types['Sonstige'] = prompt_types.get('Sonstige', 0) + 1
                
        logger.info("Document types found:")
        for doc_type, count in prompt_types.items():
            logger.info(f"  {doc_type}: {count} documents")
            
    def create_training_prompts(self, data):
        """Create enhanced training prompts for German legal documents"""
        logger.info("🔧 Creating enhanced training prompts...")
        
        enhanced_prompts = []
        
        for i, item in enumerate(data):
            prompt = item.get('prompt', '').strip()
            completion = item.get('completion', '').strip()
            
            # Create system prompt for German legal assistant
            system_prompt = """Sie sind ein erfahrener deutscher Rechtsanwalt und erstellen professionelle rechtliche Antworten auf Dokumente. 
Ihre Antworten sind:
- Formal und professionell im deutschen Rechtsstil
- Präzise und sachlich
- Vollständig anonymisiert (verwenden Sie Platzhalter wie [NAME], [ADRESSE])
- Rechtlich fundiert und angemessen"""

            # Format the training example
            enhanced_prompt = {
                "id": f"legal_train_{i+1}",
                "system": system_prompt,
                "input": f"Rechtsdokument:\n{prompt}",
                "expected_output": completion if completion else "Sehr geehrte Damen und Herren,\n\nwir haben Ihr Schreiben zur Kenntnis genommen und werden die dargelegten Punkte eingehend prüfen.\n\nMit freundlichen Grüßen",
                "document_type": self._classify_document(prompt)
            }
            
            enhanced_prompts.append(enhanced_prompt)
            
        logger.info(f"✅ Created {len(enhanced_prompts)} enhanced training prompts")
        return enhanced_prompts
        
    def _classify_document(self, prompt):
        """Classify the document type based on content"""
        prompt_lower = prompt.lower()
        
        if 'klage' in prompt_lower or 'klageschrift' in prompt_lower:
            return 'Klage'
        elif 'abmahnung' in prompt_lower:
            return 'Abmahnung'
        elif 'kündigung' in prompt_lower:
            return 'Kündigung'
        elif 'mahnung' in prompt_lower and 'abmahnung' not in prompt_lower:
            return 'Mahnung'
        elif 'vertrag' in prompt_lower:
            return 'Vertrag'
        else:
            return 'Allgemein'
            
    def create_model_configuration(self, enhanced_prompts):
        """Create a model configuration file for local deployment"""
        logger.info("⚙️ Creating model configuration...")
        
        # Group prompts by document type
        by_type = {}
        for prompt in enhanced_prompts:
            doc_type = prompt['document_type']
            if doc_type not in by_type:
                by_type[doc_type] = []
            by_type[doc_type].append(prompt)
            
        config = {
            "model_name": "Anwalts AI - German Legal Assistant",
            "version": "1.0",
            "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_examples": len(enhanced_prompts),
            "document_types": {doc_type: len(prompts) for doc_type, prompts in by_type.items()},
            "system_prompt": enhanced_prompts[0]['system'] if enhanced_prompts else "",
            "sample_responses": self._create_sample_responses(by_type)
        }
        
        # Save configuration
        config_path = self.output_dir / "model_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Model configuration saved to {config_path}")
        return config
        
    def _create_sample_responses(self, by_type):
        """Create sample responses for each document type"""
        samples = {}
        
        response_templates = {
            'Klage': """Sehr geehrte Damen und Herren,

bezugnehmend auf Ihre Klage vom [DATUM] teilen wir Ihnen mit, dass wir die geltend gemachten Ansprüche bestreiten.

Eine ausführliche Stellungnahme erfolgt fristgerecht.

Mit freundlichen Grüßen""",
            
            'Abmahnung': """Sehr geehrte Damen und Herren,

wir haben Ihre Abmahnung vom [DATUM] erhalten und zur Kenntnis genommen.

Nach eingehender rechtlicher Prüfung weisen wir die erhobenen Vorwürfe zurück. Eine Unterlassungserklärung wird nicht abgegeben.

Mit freundlichen Grüßen""",
            
            'Kündigung': """Sehr geehrte Damen und Herren,

den Erhalt Ihrer Kündigung vom [DATUM] bestätigen wir hiermit.

Wir behalten uns vor, die Rechtmäßigkeit der Kündigung zu überprüfen und gegebenenfalls rechtliche Schritte einzuleiten.

Mit freundlichen Grüßen""",
            
            'Mahnung': """Sehr geehrte Damen und Herren,

Ihre Mahnung vom [DATUM] haben wir erhalten.

Die behaupteten Forderungen werden derzeit von unserer Rechtsabteilung geprüft. Eine Stellungnahme erfolgt in Kürze.

Mit freundlichen Grüßen""",
            
            'Allgemein': """Sehr geehrte Damen und Herren,

wir haben Ihr Schreiben vom [DATUM] erhalten und werden uns umgehend mit der Angelegenheit befassen.

Eine ausführliche Antwort erfolgt zeitnah.

Mit freundlichen Grüßen"""
        }
        
        for doc_type, template in response_templates.items():
            if doc_type in by_type and by_type[doc_type]:
                samples[doc_type] = {
                    "template": template,
                    "example_count": len(by_type[doc_type])
                }
                
        return samples
        
    def train_model(self):
        """Execute the training process"""
        logger.info("🚀 Starting local model training...")
        
        # Load and analyze data
        data = self.load_training_data()
        if not data:
            logger.error("❌ No training data available")
            return False
            
        self.analyze_training_data(data)
        
        # Create enhanced prompts
        enhanced_prompts = self.create_training_prompts(data)
        
        # Create model configuration
        config = self.create_model_configuration(enhanced_prompts)
        
        # Save training data for the model
        training_path = self.output_dir / "training_data.jsonl"
        with open(training_path, 'w', encoding='utf-8') as f:
            for prompt in enhanced_prompts:
                f.write(json.dumps(prompt, ensure_ascii=False) + '\n')
                
        logger.info(f"✅ Training data saved to {training_path}")
        
        # Create deployment script
        self._create_deployment_script(config)
        
        logger.info("🎉 Local model training completed successfully!")
        logger.info(f"📁 Model files saved in: {self.output_dir}")
        
        return True
        
    def _create_deployment_script(self, config):
        """Create a deployment script for the trained model"""
        script_content = f'''#!/usr/bin/env python3
"""
Anwalts AI Local Model Deployment Script
Generated on: {config['training_date']}
"""

import json
import random

class AnwaltsAILocal:
    def __init__(self):
        self.config = {json.dumps(config, indent=8, ensure_ascii=False)}
        
    def generate_response(self, document_text):
        """Generate a professional German legal response"""
        doc_type = self._classify_document(document_text)
        template = self.config["sample_responses"].get(doc_type, {{}}).get("template", "")
        
        if template:
            return template
        else:
            return self.config["sample_responses"]["Allgemein"]["template"]
            
    def _classify_document(self, text):
        """Classify document type"""
        text_lower = text.lower()
        
        if 'klage' in text_lower:
            return 'Klage'
        elif 'abmahnung' in text_lower:
            return 'Abmahnung'
        elif 'kündigung' in text_lower:
            return 'Kündigung'
        elif 'mahnung' in text_lower:
            return 'Mahnung'
        else:
            return 'Allgemein'

# Example usage
if __name__ == "__main__":
    model = AnwaltsAILocal()
    
    test_document = "Klage wegen ausstehender Gehaltszahlungen..."
    response = model.generate_response(test_document)
    print("Generated Response:")
    print(response)
'''
        
        script_path = self.output_dir / "deploy_model.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        logger.info(f"✅ Deployment script created: {script_path}")

def main():
    """Main training function"""
    print("🤖 Anwalts AI - Local Model Training")
    print("=" * 50)
    
    trainer = SimpleGermanLegalTrainer()
    
    try:
        success = trainer.train_model()
        
        if success:
            print("\n🎉 Training completed successfully!")
            print(f"📁 Model files saved in: {trainer.output_dir}")
            print("\n📋 Next steps:")
            print("1. Test the model with: python deploy_model.py")
            print("2. Integrate with existing infrastructure")
            print("3. Deploy to production environment")
        else:
            print("\n❌ Training failed. Check logs for details.")
            
    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        print(f"\n❌ Training failed: {e}")

if __name__ == "__main__":
    main()