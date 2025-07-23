#!/usr/bin/env python3
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
                    text = f"Prompt: {item['prompt']}\n\nAntwort: {item.get('completion', '')}"
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
