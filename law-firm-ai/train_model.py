#!/usr/bin/env python3
"""
Training script for fine-tuning DeepSeek-V3 model with German legal documents.
Optimized for cost efficiency and performance.
"""

import json
import logging
import time
from datetime import datetime
from together import Together

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
TOGETHER_API_KEY = "REDACTED"
BASE_MODEL = "deepseek-ai/DeepSeek-V3"
TRAINING_DATA_PATH = "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law_firm_dataset.json"

# Initialize Together client
client = Together(api_key=TOGETHER_API_KEY)

def load_and_prepare_dataset():
    """Load and prepare the training dataset for fine-tuning."""
    logger.info("Loading training dataset...")
    
    with open(TRAINING_DATA_PATH, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    logger.info(f"Loaded {len(raw_data)} raw examples")
    
    # Filter out examples with empty responses
    filtered_data = [item for item in raw_data if item.get('response', '').strip()]
    
    if not filtered_data:
        # Since all responses are empty, we need to generate them
        logger.info("No responses found in dataset. Generating responses using base model...")
        return generate_training_responses(raw_data[:50])  # Limit to 50 for cost efficiency
    
    logger.info(f"Found {len(filtered_data)} examples with responses")
    return filtered_data

def generate_training_responses(raw_data):
    """Generate responses using the base model for training examples."""
    training_data = []
    
    system_prompt = """Sie sind ein erfahrener deutscher Rechtsassistent. Analysieren Sie das Dokument und erstellen Sie eine strukturierte rechtliche Ersteinschätzung."""
    
    for i, item in enumerate(raw_data):
        try:
            logger.info(f"Generating response {i+1}/{len(raw_data)}")
            
            response = client.chat.completions.create(
                model=BASE_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analysieren Sie dieses Dokument:\n\n{item['prompt']}"}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            generated_response = response.choices[0].message.content
            
            training_data.append({
                "prompt": item['prompt'],
                "response": generated_response
            })
            
            # Add delay to avoid rate limits
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to generate response for example {i+1}: {e}")
            continue
    
    logger.info(f"Generated {len(training_data)} training examples")
    
    # Save generated training data
    with open('generated_training_data.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    return training_data

def format_for_together_training(data):
    """Format data for Together AI fine-tuning format."""
    formatted_data = []
    
    for item in data:
        formatted_item = {
            "messages": [
                {
                    "role": "system", 
                    "content": "Sie sind ein erfahrener deutscher Rechtsassistent mit Expertise in verschiedenen Rechtsgebieten."
                },
                {
                    "role": "user", 
                    "content": f"Analysieren Sie bitte das folgende rechtliche Dokument:\n\n{item['prompt']}"
                },
                {
                    "role": "assistant", 
                    "content": item['response']
                }
            ]
        }
        formatted_data.append(formatted_item)
    
    return formatted_data

def create_training_file(formatted_data):
    """Create and upload training file to Together AI."""
    logger.info("Creating training file...")
    
    # Save formatted training data as JSONL
    training_file_path = "legal_training_data.jsonl"
    with open(training_file_path, 'w', encoding='utf-8') as f:
        for item in formatted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    logger.info(f"Saved training data to {training_file_path}")
    
    try:
        # Upload file to Together AI
        with open(training_file_path, 'rb') as f:
            file_response = client.files.upload(
                file=f,
                purpose="fine-tune"
            )
        
        logger.info(f"Uploaded training file: {file_response.id}")
        return file_response.id
        
    except Exception as e:
        logger.error(f"Failed to upload training file: {e}")
        return None

def start_fine_tuning(file_id):
    """Start the fine-tuning job."""
    logger.info("Starting fine-tuning job...")
    
    try:
        fine_tune_response = client.fine_tuning.jobs.create(
            training_file=file_id,
            model=BASE_MODEL,
            hyperparameters={
                "learning_rate": 1e-5,
                "batch_size": 4,
                "epochs": 3,
                "warmup_ratio": 0.1
            },
            suffix="legal-assistant-v1"
        )
        
        logger.info(f"Fine-tuning job started: {fine_tune_response.id}")
        return fine_tune_response.id
        
    except Exception as e:
        logger.error(f"Failed to start fine-tuning: {e}")
        return None

def monitor_training(job_id):
    """Monitor the training progress."""
    logger.info(f"Monitoring training job: {job_id}")
    
    while True:
        try:
            job = client.fine_tuning.jobs.retrieve(job_id)
            status = job.status
            
            logger.info(f"Training status: {status}")
            
            if status == "succeeded":
                logger.info(f"Training completed! Model ID: {job.fine_tuned_model}")
                return job.fine_tuned_model
            elif status == "failed":
                logger.error("Training failed!")
                return None
            elif status in ["cancelled", "validating_files"]:
                logger.warning(f"Training status: {status}")
                return None
            
            # Wait before checking again
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"Error monitoring training: {e}")
            time.sleep(60)

def main():
    """Main training pipeline."""
    logger.info("Starting legal document model training pipeline...")
    
    try:
        # Step 1: Load and prepare dataset
        training_data = load_and_prepare_dataset()
        
        if not training_data:
            logger.error("No training data available")
            return
        
        # Step 2: Format for Together AI
        formatted_data = format_for_together_training(training_data)
        logger.info(f"Formatted {len(formatted_data)} training examples")
        
        # Step 3: Create and upload training file
        file_id = create_training_file(formatted_data)
        
        if not file_id:
            logger.error("Failed to upload training file")
            return
        
        # Step 4: Start fine-tuning
        job_id = start_fine_tuning(file_id)
        
        if not job_id:
            logger.error("Failed to start fine-tuning")
            return
        
        # Step 5: Monitor training
        model_id = monitor_training(job_id)
        
        if model_id:
            logger.info(f"Training completed successfully!")
            logger.info(f"Fine-tuned model ID: {model_id}")
            
            # Save model info
            model_info = {
                "model_id": model_id,
                "base_model": BASE_MODEL,
                "training_completed": datetime.now().isoformat(),
                "training_data_size": len(formatted_data)
            }
            
            with open("trained_model_info.json", "w", encoding="utf-8") as f:
                json.dump(model_info, f, ensure_ascii=False, indent=2)
            
            logger.info("Model information saved to trained_model_info.json")
        else:
            logger.error("Training failed or was cancelled")
    
    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")

if __name__ == "__main__":
    main()