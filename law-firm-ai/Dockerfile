# FILE: Dockerfile

# Zero-Trust Sanitization Architecture - Secure Dockerfile
FROM python:3.10-slim

USER root

# Install system dependencies including OpenCV requirements
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    poppler-utils \
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download multiple spaCy models for robust NER
RUN python -m spacy download de_core_news_sm && \
    python -m spacy download de_core_news_md

# Attempt to download large model (may fail in resource-constrained environments)
RUN python -m spacy download de_core_news_lg || echo "Large model download failed - using medium model"

# Copy application files
COPY secure_sanitizer.py .
COPY sanitizer_app.py .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash sanitizer && \
    chown -R sanitizer:sanitizer /app

USER sanitizer

EXPOSE 5001

# Environment variables for security
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false

# Run the secure sanitizer with translation support
CMD ["python", "secure_sanitizer.py"]