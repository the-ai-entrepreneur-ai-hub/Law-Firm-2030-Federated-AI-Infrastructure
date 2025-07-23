# Local LLM Training Environment
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Install Python dependencies for training
RUN pip install \
    transformers \
    datasets \
    accelerate \
    peft \
    bitsandbytes \
    torch \
    tqdm \
    wandb \
    huggingface_hub

# Create working directory
WORKDIR /app

# Copy training scripts and data
COPY . /app/

# Expose Ollama port
EXPOSE 11434

# Start Ollama service
CMD ["ollama", "serve"]
