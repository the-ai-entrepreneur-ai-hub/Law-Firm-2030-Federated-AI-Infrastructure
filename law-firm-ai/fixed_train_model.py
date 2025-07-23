#!/usr/bin/env python3
"""
FIXED Training script for fine-tuning with German legal documents.
Addresses critical issues with the original implementation.
"""

import json
import logging
import time
import os
from datetime import datetime
from together import Together

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FIXED Configuration - Use supported fine-tuning model
TOGETHER_API_KEY = "REDACTED"
SUPPORTED_MODELS = [
    "meta-llama/Llama-3.2-3B-Instruct-Turbo",
    "meta-llama/Llama-3.1-8B-Instruct-Turbo", 
    "meta-llama/Llama-3.1-70B-Instruct-Turbo"
]
FINE_TUNE_MODEL = SUPPORTED_MODELS[1]  # Use 8B model for cost efficiency
INFERENCE_MODEL = "deepseek-ai/DeepSeek-V3"  # Keep DeepSeek for inference
TRAINING_DATA_PATH = "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law_firm_dataset.json"

# Initialize Together client
client = Together(api_key=TOGETHER_API_KEY)

def check_fine_tuning_support():
    """Check which models support fine-tuning on Together AI."""
    logger.info("Checking fine-tuning support...")
    
    try:
        # This would list available models for fine-tuning
        models = client.models.list()
        fine_tune_models = [model.id for model in models if hasattr(model, 'fine_tunable') and model.fine_tunable]
        logger.info(f"Models supporting fine-tuning: {fine_tune_models[:5]}...")  # Show first 5
        return fine_tune_models
    except Exception as e:
        logger.warning(f"Could not check model support: {e}")
        return SUPPORTED_MODELS

def create_high_quality_training_sample():
    """Create a small, high-quality training dataset manually."""
    logger.info("Creating high-quality training samples...")
    
    training_samples = [
        {
            "messages": [
                {
                    "role": "system",
                    "content": "Sie sind ein erfahrener deutscher Rechtsassistent mit Expertise in verschiedenen Rechtsgebieten. Analysieren Sie rechtliche Dokumente und erstellen Sie strukturierte Ersteinschätzungen."
                },
                {
                    "role": "user", 
                    "content": "Analysieren Sie bitte das folgende rechtliche Dokument:\n\nAn das Amtsgericht München\nMusterstraße 1\n80331 München\n\n**Klageerhebung**\n\nSehr geehrte Damen und Herren,\n\nin der Angelegenheit Max Mustermann gegen Musterfirma GmbH erheben wir Klage wegen ausstehender Gehaltszahlungen.\nUnser Mandant, Max Mustermann, wohnhaft in München, hat seit drei Monaten kein Gehalt erhalten.\n\nWir beantragen, die Beklagte zu verurteilen, an unseren Mandanten 3000 EUR nebst Zinsen zu zahlen.\n\nMit freundlichen Grüßen,\nAnwaltskanzlei Legal Eagles"
                },
                {
                    "role": "assistant",
                    "content": "**📋 BETREFF:** Lohnklage gegen Musterfirma GmbH - 3.000 EUR Gehaltszahlung\n\n**📄 1. SACHVERHALT:**\n• Arbeitsrechtliche Streitigkeit zwischen Arbeitnehmer und Arbeitgeber\n• Beteiligte: Max Mustermann (Kläger) vs. Musterfirma GmbH (Beklagte)\n• Streitwert: 3.000 EUR zzgl. Zinsen\n• Zeitraum: 3 Monate ausstehende Gehaltszahlungen\n• Zuständigkeit: Amtsgericht München\n\n**⚖️ 2. RECHTLICHE BEWERTUNG:**\n• Rechtsgebiet: Arbeitsrecht, §§ 611-630 BGB\n• Rechtslage: Arbeitgeber ist zur pünktlichen Lohnzahlung verpflichtet (§ 614 BGB)\n• Anspruchsgrundlage: Entgeltfortzahlungsanspruch aus Arbeitsvertrag\n• Erfolgsaussichten: Bei nachweisbarem Arbeitsverhältnis sehr gut\n\n**🎯 3. EMPFOHLENE MASSNAHMEN:**\n• Sofortige Schritte: Arbeitsvertrag und Lohnabrechnungen sichern\n• Fristen: Klagefrist beachten (3 Jahre Verjährung § 195 BGB)\n• Weitere Unterlagen: Arbeitsvertrag, Gehaltsabrechnungen, Arbeitszeiten\n• Mandantenkontakt: Vollmacht prüfen, Prozesskostenhilfe erwägen\n\n**⚠️ 4. BESONDERE HINWEISE:**\nVerzugszinsen ab Fälligkeit (§ 288 BGB), eventuelle Schadensersatzansprüche prüfen. Bei längerer Nichtzahlung auch außerordentliche Kündigung möglich."
                }
            ]
        },
        {
            "messages": [
                {
                    "role": "system",
                    "content": "Sie sind ein erfahrener deutscher Rechtsassistent mit Expertise in verschiedenen Rechtsgebieten. Analysieren Sie rechtliche Dokumente und erstellen Sie strukturierte Ersteinschätzungen."
                },
                {
                    "role": "user",
                    "content": "Analysieren Sie bitte das folgende rechtliche Dokument:\n\nAn Prof. Dr. Schmidt\nLöchelstraße 54\n10115 Berlin\n\n**Abmahnung wegen Urheberrechtsverletzung**\n\nSehr geehrte/r Prof. Dr. Schmidt,\n\nwir vertreten die Interessen der Foto AG. Sie haben am 15.01.2024 auf Ihrer Website www.schmidt-consulting.de ein Bild verwendet, an dem unsere Mandantin die ausschließlichen Nutzungsrechte besitzt.\n\nWir fordern Sie auf, das Bild sofort zu entfernen und eine strafbewehrte Unterlassungserklärung abzugeben.\n\nMit freundlichen Grüßen,\nAnwaltskanzlei Legal Eagles"
                },
                {
                    "role": "assistant", 
                    "content": "**📋 BETREFF:** Urheberrechtsabmahnung - Bildnutzung ohne Lizenz\n\n**📄 1. SACHVERHALT:**\n• Urheberrechtsverletzung durch unerlaubte Bildnutzung\n• Beteiligte: Foto AG (Rechteinhaber) vs. Prof. Dr. Schmidt (Verletzer)\n• Verletzungshandlung: Veröffentlichung auf Website am 15.01.2024\n• Gegenstand: Bild mit ausschließlichen Nutzungsrechten\n• Forderung: Entfernung + Unterlassungserklärung\n\n**⚖️ 2. RECHTLICHE BEWERTUNG:**\n• Rechtsgebiet: Urheberrecht, §§ 15 ff. UrhG\n• Rechtslage: Unerlaubte Nutzung verletzt Verwertungsrechte (§ 15 UrhG)\n• Anspruchsgrundlagen: Unterlassung (§ 97 UrhG), Schadensersatz (§ 97 Abs. 2 UrhG)\n• Risiken: Weitere Abmahnkosten, Schadensersatzforderungen möglich\n• Erfolgsaussichten der Gegenseite: Hoch bei nachweisbaren Rechten\n\n**🎯 3. EMPFOHLENE MASSNAHMEN:**\n• Sofortige Schritte: Bild umgehend von Website entfernen\n• Fristen: Reaktionsfrist der Abmahnung beachten (meist 7-14 Tage)\n• Weitere Unterlagen: Screenshot der Website, Lizenzrechte prüfen\n• Mandantenkontakt: Rechtmäßigkeit der Bildnutzung klären\n\n**⚠️ 4. BESONDERE HINWEISE:**\nModifizierte Unterlassungserklärung statt Originalformular verwenden. Lizenzschaden oder entgangener Gewinn können geltend gemacht werden. Bei berechtigter Abmahnung schnelle Reaktion kostenmindernd."
                }
            ]
        }
    ]
    
    # Save high-quality samples
    with open('high_quality_training_data.jsonl', 'w', encoding='utf-8') as f:
        for sample in training_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    logger.info(f"Created {len(training_samples)} high-quality training examples")
    return training_samples

def test_together_api():
    """Test the Together API connection and capabilities."""
    logger.info("Testing Together API connection...")
    
    try:
        # Test inference
        response = client.chat.completions.create(
            model=INFERENCE_MODEL,
            messages=[
                {"role": "user", "content": "Hello, can you help with German legal analysis?"}
            ],
            max_tokens=100
        )
        
        logger.info("✓ Inference API working")
        logger.info(f"Response: {response.choices[0].message.content[:100]}...")
        
        # Test file upload capability
        test_data = {"messages": [{"role": "user", "content": "test"}]}
        with open('test_upload.jsonl', 'w') as f:
            f.write(json.dumps(test_data) + '\n')
        
        try:
            file_response = client.files.upload(
                file='test_upload.jsonl',
                purpose="fine-tune"
            )
            logger.info("✓ File upload working")
            
            # Clean up test file
            try:
                client.files.delete(file_response.id)
                os.remove('test_upload.jsonl')
            except:
                pass
                
        except Exception as e:
            logger.warning(f"File upload test failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"API test failed: {e}")
        return False

def start_fine_tuning_safe():
    """Start fine-tuning with proper error handling and model validation."""
    logger.info("Starting safe fine-tuning process...")
    
    # Step 1: Test API
    if not test_together_api():
        logger.error("API test failed - aborting fine-tuning")
        return None
    
    # Step 2: Check model support
    supported_models = check_fine_tuning_support()
    
    if FINE_TUNE_MODEL not in supported_models:
        logger.warning(f"Model {FINE_TUNE_MODEL} may not support fine-tuning")
        logger.info("Proceeding with standard Llama model...")
        model_to_use = "meta-llama/Llama-3.1-8B-Instruct-Turbo"  # Known to work
    else:
        model_to_use = FINE_TUNE_MODEL
    
    # Step 3: Create training data
    training_data = create_high_quality_training_sample()
    
    # Step 4: Upload training file
    try:
        file_response = client.files.upload(
            file='high_quality_training_data.jsonl',
            purpose="fine-tune"
        )
        
        logger.info(f"Training file uploaded: {file_response.id}")
        
        # Step 5: Create fine-tuning job with CORRECTED API call
        try:
            fine_tune_response = client.fine_tuning.create(  # FIXED: Correct method
                training_file=file_response.id,
                model=model_to_use,
                hyperparameters={
                    "learning_rate": 1e-5,
                    "batch_size": 2,  # Smaller batch for cost efficiency
                    "epochs": 2,  # Fewer epochs for initial test
                },
                suffix="legal-assistant-test"
            )
            
            logger.info(f"Fine-tuning job created: {fine_tune_response.id}")
            return fine_tune_response.id
            
        except Exception as e:
            logger.error(f"Fine-tuning creation failed: {e}")
            logger.info("This might be due to model support limitations")
            return None
            
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return None

def monitor_training_safe(job_id):
    """Monitor training with proper error handling."""
    if not job_id:
        return None
        
    logger.info(f"Monitoring training job: {job_id}")
    
    max_checks = 60  # Maximum 30 minutes of checking
    check_count = 0
    
    while check_count < max_checks:
        try:
            job = client.fine_tuning.retrieve(job_id)  # FIXED: Correct method
            status = job.status
            
            logger.info(f"Training status: {status} (Check {check_count + 1})")
            
            if status == "succeeded":
                logger.info(f"🎉 Training completed! Model ID: {job.fine_tuned_model}")
                
                # Save model info
                model_info = {
                    "model_id": job.fine_tuned_model,
                    "base_model": job.model,
                    "training_completed": datetime.now().isoformat(),
                    "job_id": job_id,
                    "status": "completed"
                }
                
                with open("trained_model_info.json", "w", encoding="utf-8") as f:
                    json.dump(model_info, f, ensure_ascii=False, indent=2)
                
                return job.fine_tuned_model
                
            elif status in ["failed", "cancelled"]:
                logger.error(f"Training failed with status: {status}")
                return None
            
            # Wait before next check
            time.sleep(30)
            check_count += 1
            
        except Exception as e:
            logger.error(f"Error checking training status: {e}")
            check_count += 1
            time.sleep(30)
    
    logger.warning("Training monitoring timed out")
    return None

def main():
    """Main execution with comprehensive error handling."""
    logger.info("🚀 Starting FIXED Together AI Fine-tuning Process")
    logger.info("=" * 60)
    
    try:
        # Start safe fine-tuning
        job_id = start_fine_tuning_safe()
        
        if job_id:
            logger.info("Fine-tuning job started successfully!")
            logger.info("You can monitor progress or check back later.")
            
            # Optional: Monitor training (comment out to run async)
            model_id = monitor_training_safe(job_id)
            
            if model_id:
                logger.info("🎉 FINE-TUNING COMPLETED SUCCESSFULLY!")
                logger.info(f"New model available: {model_id}")
            else:
                logger.info("Training is still in progress or failed.")
                logger.info(f"You can check status later with job ID: {job_id}")
        else:
            logger.error("❌ Fine-tuning could not be started")
            logger.info("Common issues:")
            logger.info("- Model doesn't support fine-tuning")
            logger.info("- API quota exceeded")
            logger.info("- Data format issues")
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()