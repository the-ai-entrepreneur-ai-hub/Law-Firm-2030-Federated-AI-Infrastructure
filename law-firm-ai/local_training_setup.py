#!/usr/bin/env python3
"""
Local Model Training Setup for German Legal Documents
Sets up Ollama/LLaMA for local training with anonymized data
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalModelTrainer:
    """
    Sets up local model training using Ollama or similar local LLM frameworks
    """
    
    def __init__(self):
        self.base_dir = Path("/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030")
        self.docker_dir = self.base_dir / "law-firm-ai"
        self.training_data = self.base_dir / "law_firm_dataset.jsonl"
        
    def check_system_requirements(self) -> Dict[str, bool]:
        """Check system requirements for local training"""
        logger.info("🔍 Checking system requirements...")
        
        requirements = {
            "docker": False,
            "nvidia_runtime": False,
            "sufficient_memory": False,
            "training_data": False
        }
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                requirements["docker"] = True
                logger.info("✅ Docker available")
        except FileNotFoundError:
            logger.error("❌ Docker not found")
        
        # Check NVIDIA runtime
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if "nvidia" in result.stdout.lower():
                requirements["nvidia_runtime"] = True
                logger.info("✅ NVIDIA Docker runtime available")
        except Exception:
            logger.warning("⚠️ NVIDIA runtime check failed")
        
        # Check memory (simplified)
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = f.read()
                if "MemTotal:" in meminfo:
                    mem_kb = int(meminfo.split("MemTotal:")[1].split()[0])
                    mem_gb = mem_kb / (1024 * 1024)
                    if mem_gb >= 8:  # Minimum 8GB RAM
                        requirements["sufficient_memory"] = True
                        logger.info(f"✅ Sufficient memory: {mem_gb:.1f}GB")
                    else:
                        logger.warning(f"⚠️ Low memory: {mem_gb:.1f}GB (8GB+ recommended)")
        except Exception:
            logger.warning("⚠️ Could not check memory")
        
        # Check training data
        if self.training_data.exists():
            requirements["training_data"] = True
            logger.info("✅ Training data found")
        else:
            logger.error("❌ Training data not found")
        
        return requirements
    
    def generate_docker_setup(self) -> str:
        """Generate Docker setup for local training"""
        
        dockerfile_content = """# Local LLM Training Environment
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    wget \\
    build-essential \\
    python3-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Install Python dependencies for training
RUN pip install \\
    transformers \\
    datasets \\
    accelerate \\
    peft \\
    bitsandbytes \\
    torch \\
    tqdm \\
    wandb \\
    huggingface_hub

# Create working directory
WORKDIR /app

# Copy training scripts and data
COPY . /app/

# Expose Ollama port
EXPOSE 11434

# Start Ollama service
CMD ["ollama", "serve"]
"""
        
        docker_compose_content = """version: '3.8'

services:
  local-trainer:
    build: .
    container_name: law-firm-local-trainer
    ports:
      - "11434:11434"
      - "5002:5002"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - TRANSFORMERS_CACHE=/app/cache
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped
"""
        
        return dockerfile_content, docker_compose_content
    
    def create_training_script(self) -> str:
        """Create local training script"""
        
        training_script = """#!/usr/bin/env python3
'''
Local Model Training Script for German Legal Documents
Uses LoRA fine-tuning for efficient local training
'''

import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalGermanLegalTrainer:
    def __init__(self):
        # Use a smaller German model for local training
        self.model_name = "microsoft/DialoGPT-medium"  # Can be replaced with German model
        self.max_length = 512
        self.output_dir = "/app/models/trained-german-legal"
        
    def load_training_data(self, data_path: str):
        '''Load and prepare training data'''
        logger.info(f"Loading training data from {data_path}")
        
        data = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    # Format for language modeling
                    text = f"Prompt: {item['prompt']}\\n\\nAntwort: {item.get('completion', '')}"
                    data.append({"text": text})
        
        return Dataset.from_list(data)
    
    def setup_model_and_tokenizer(self):
        '''Setup model and tokenizer with LoRA'''
        logger.info("Setting up model and tokenizer...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # LoRA configuration for efficient training
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj"]
        )
        
        self.model = get_peft_model(self.model, lora_config)
        logger.info("✅ Model setup complete with LoRA")
    
    def tokenize_data(self, dataset):
        '''Tokenize the dataset'''
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=self.max_length,
                return_tensors="pt"
            )
        
        return dataset.map(tokenize_function, batched=True)
    
    def train_model(self, dataset):
        '''Train the model'''
        logger.info("Starting model training...")
        
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            learning_rate=5e-5,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="no",
            save_total_limit=2,
            fp16=torch.cuda.is_available(),
            dataloader_pin_memory=False,
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        trainer.train()
        trainer.save_model()
        logger.info(f"✅ Training complete! Model saved to {self.output_dir}")

def main():
    trainer = LocalGermanLegalTrainer()
    
    # Setup model
    trainer.setup_model_and_tokenizer()
    
    # Load and tokenize data
    dataset = trainer.load_training_data("/app/data/law_firm_dataset.jsonl")
    tokenized_dataset = trainer.tokenize_data(dataset)
    
    # Train model
    trainer.train_model(tokenized_dataset)
    
    print("🎉 Local model training completed!")

if __name__ == "__main__":
    main()
"""
        
        return training_script

def main():
    """Main setup function"""
    trainer = LocalModelTrainer()
    
    print("🚀 Local Model Training Setup")
    print("=" * 50)
    
    # Check requirements
    requirements = trainer.check_system_requirements()
    
    print("\\n📋 System Requirements:")
    for req, status in requirements.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {req}: {'OK' if status else 'Missing'}")
    
    if not all(requirements.values()):
        print("\\n⚠️ Some requirements are missing. Training may not work optimally.")
    
    # Generate Docker setup files
    dockerfile, docker_compose = trainer.generate_docker_setup()
    training_script = trainer.create_training_script()
    
    # Save files
    docker_dir = trainer.docker_dir
    
    # Create local training directory
    local_training_dir = docker_dir / "local-training"
    local_training_dir.mkdir(exist_ok=True)
    
    # Write Docker files
    (local_training_dir / "Dockerfile").write_text(dockerfile)
    (local_training_dir / "docker-compose.yml").write_text(docker_compose)
    (local_training_dir / "train_local.py").write_text(training_script)
    
    print(f"\\n📁 Setup files created in: {local_training_dir}")
    print("\\n🔧 Next steps:")
    print("1. cd law-firm-ai/local-training")
    print("2. docker-compose up --build")
    print("3. docker exec -it law-firm-local-trainer python train_local.py")
    
    return True

if __name__ == "__main__":
    main()