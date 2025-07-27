# Fine-Tuning a Language Model on Google Colab with Unsloth

This guide provides a step-by-step walkthrough for fine-tuning a language model using Unsloth on a free Google Colab instance. We will use the `unsloth/Phi-3-mini-4k-instruct-bnb-4bit` model as an example.

## Why Fine-Tune?

Fine-tuning adapts a pre-trained model to a specific task or domain (like legal document analysis, customer support, etc.), significantly improving its performance and relevance for your use case.

## Why Unsloth?

[Unsloth](https://github.com/unslothai/unsloth) is a powerful library that dramatically speeds up fine-tuning and reduces memory usage. This makes it possible to fine-tune modern language models on free-tier Google Colab GPUs.

---

### Step 1: Setup Google Colab Environment

First, ensure your Colab notebook is using a GPU. Go to **Runtime > Change runtime type** and select **T4 GPU** from the dropdown.

Next, install the necessary libraries. Unsloth handles the installation of most dependencies like `torch`, `transformers`, and `peft`.

```python
# Install Unsloth and other required packages
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install "git+https://github.com/huggingface/transformers.git"
!pip install --no-deps "trl<0.9.0" "peft<0.11.0" "accelerate<0.30.0" "bitsandbytes<0.44.0"
```

---

### Step 2: Load the Model and Tokenizer

We will use the `FastLanguageModel` from Unsloth to load our model and tokenizer. This class automatically applies performance optimizations.

```python
from unsloth import FastLanguageModel
import torch

# Model configuration
max_seq_length = 2048 # Choose any value that fits your needs
dtype = None # None for auto-detection. Other options: torch.float16, torch.bfloat16, torch.float32
load_in_4bit = True # Use 4-bit quantization to reduce memory usage

# Load the model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Phi-3-mini-4k-instruct-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)
```

---

### Step 3: Prepare Your Dataset

Your dataset needs to be in a format that the trainer can understand. A common format is a list of conversations or instructions. For Phi-3, the instruction format is specific.

**Example Data Formatting:**

```python
# This is the required format for Phi-3 instruct models
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

# Function to format your data
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = alpaca_prompt.format(instruction, input, output)
        texts.append(text)
    return { "text" : texts, }
pass

# Load your dataset from Hugging Face or a local file
from datasets import load_dataset
dataset = load_dataset("your_dataset_name", split = "train") # Replace with your dataset
dataset = dataset.map(formatting_prompts_func, batched = True,)
```

*Note: If you have a local file like `legal_training_dataset.jsonl`, you can load it using `load_dataset("json", data_files="legal_training_dataset.jsonl")`.*

---

### Step 4: Fine-Tune the Model

Now, we configure the model for training using PEFT (Parameter-Efficient Fine-Tuning) with LoRA (Low-Rank Adaptation) and use the `SFTTrainer` from the TRL library.

```python
from trl import SFTTrainer
from transformers import TrainingArguments

# Configure PEFT with LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # LoRA rank
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = True,
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# Configure the trainer
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # Can make training faster for short sequences
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Set the number of training steps
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

# Start training
trainer.train()
```

---

### Step 5: Save and Test the Model

After training, you can save the fine-tuned model adapters. For inference, you can merge them into the original model.

```python
# Save the LoRA adapters
model.save_pretrained("lora_model")

# To run inference, load the base model and apply the adapters
from peft import PeftModel
base_model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Phi-3-mini-4k-instruct-bnb-4bit"
)
model = PeftModel.from_pretrained(base_model, "lora_model")

# Test with a prompt
inputs = tokenizer(
[
    alpaca_prompt.format(
        "Analyze the following legal clause.", # instruction
        "The party of the first part shall not be held liable for damages arising from acts of God.", # input
        "", # output - leave empty for the model to generate
    )
], return_tensors = "pt").to("cuda")

outputs = model.generate(**inputs, max_new_tokens = 128, use_cache = True)
print(tokenizer.batch_decode(outputs))
```

---

## Model Recommendation for a Human-in-the-Loop System

For your goal of using a free model that can be improved with user feedback, your choice of **`unsloth/Phi-3-mini-4k-instruct-bnb-4bit`** is excellent.

**Why Phi-3 Mini is a great choice:**
*   **High Performance:** It's one of the best-performing models in its size class, rivaling much larger models.
*   **Efficient:** It's small enough to be fine-tuned quickly on free hardware, making it ideal for iterative development.
*   **Instruction Tuned:** It's already been trained to follow instructions, which provides a great starting point for fine-tuning on your specific tasks.

### Implementing a Human-in-the-Loop System

A "human-in-the-loop" system is not about a specific model, but about the process you build around it. Here’s how it works:

1.  **Initial Fine-Tuning:** Train your model on an initial, high-quality dataset (like your `legal_training_dataset.jsonl`).
2.  **Deploy & Collect Feedback:** Deploy the model (even in a test environment) and have users interact with it. Log the prompts and the model's generated responses.
3.  **Review and Curate:** Have a human expert review the model's responses. Identify where it performed well and where it failed.
4.  **Create a New Dataset:** Convert the collected feedback into a new training dataset. This dataset should contain corrected responses, new examples of difficult cases, or preference data (e.g., "Response A is better than Response B").
5.  **Re-train the Model:** Fine-tune your model again using this new, curated dataset. This will help it learn from its mistakes and improve its performance on the tasks your users care about.
6.  **Repeat:** This is a continuous cycle. The more feedback you collect and incorporate, the better the model will become over time.

This iterative process of training, feedback, and re-training is the core of building a powerful, specialized AI model.

### Future Steps: Docker

Once you have a fine-tuned model you are happy with, you can save the fully merged model and package it into a Docker container with a simple API (like Flask or FastAPI) to serve it. This will make it portable and easy to deploy.