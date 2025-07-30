from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# Step 1: Load the Model and Tokenizer
# =======================================
max_seq_length = 2048
dtype = None  # Autodetect
load_in_4bit = True # Use 4-bit quantization for efficiency

print("Loading model and tokenizer...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Phi-3-mini-4k-instruct-bnb-4bit",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)
print("Model and tokenizer loaded successfully.")

# Step 2: Prepare Your Dataset
# ============================
# This is the required prompt format for the Phi-3 instruct model.
# It structures the data so the model knows what the instruction, input, and expected response are.
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def formatting_prompts_func(examples):
    """
    This function formats the dataset examples into the alpaca_prompt format.
    It assumes your JSONL file has 'instruction', 'input', and 'output' fields.
    """
    instructions = examples.get("instruction", [])
    inputs       = examples.get("input", [])
    outputs      = examples.get("output", [])
    texts = []
    for instruction, input_text, output_text in zip(instructions, inputs, outputs):
        text = alpaca_prompt.format(instruction, input_text, output_text)
        texts.append(text)
    return { "text": texts }

# Load your local dataset.
# Ensure 'legal_training_dataset.jsonl' is in the project root or provide a full path.
print("Loading and formatting dataset...")
dataset = load_dataset("json", data_files="../legal_training_dataset.jsonl", split="train")
dataset = dataset.map(formatting_prompts_func, batched=True)
print("Dataset prepared successfully.")


# Step 3: Configure PEFT/LoRA for Fine-Tuning
# ============================================
# Parameter-Efficient Fine-Tuning (PEFT) with Low-Rank Adaptation (LoRA)
# allows us to train the model efficiently without modifying all its weights.
print("Configuring model for PEFT/LoRA...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=3407,
)
print("Model configured for training.")


# Step 4: Configure and Run the SFTTrainer
# ========================================
print("Setting up the trainer...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,  # Can be set to True for short sequences to speed up training
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,  # Adjust based on your dataset size and desired training time
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs", # Directory to save training outputs
    ),
)

# Start the training process
print("Starting model training...")
trainer.train()
print("Training complete.")


# Step 5: Save the Fine-Tuned Model
# =================================
# This saves the trained LoRA adapters, not the full model.
print("Saving fine-tuned model adapters...")
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")
print("Model adapters saved to 'lora_model' directory inside 'law-firm-ai/'.")