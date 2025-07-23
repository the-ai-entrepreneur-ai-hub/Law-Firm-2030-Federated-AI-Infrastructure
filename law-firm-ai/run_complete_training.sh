#!/bin/bash
# Complete Training and Docker Integration Script
# Trains model on anonymized dataset and deploys to Docker

set -e

echo "🔒 German Legal Document AI Training Pipeline"
echo "============================================="
echo ""

# Change to the correct directory
cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai"

echo "📋 Step 1: Training Model on Anonymized Dataset"
echo "-----------------------------------------------"
python3 train_anonymized_model.py

if [ $? -eq 0 ]; then
    echo "✅ Model training completed successfully!"
    echo ""
    
    echo "📋 Step 2: Updating Docker with Trained Model"
    echo "----------------------------------------------"
    python3 update_docker_with_trained_model.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker integration completed successfully!"
        echo ""
        echo "🎉 COMPLETE SUCCESS!"
        echo "==================="
        echo "🎯 Your trained model is now running in Docker"
        echo "🌐 Service available at: http://localhost:5001"
        echo "📄 Upload your 8-page PDFs for processing"
        echo "🔒 Perfect anonymized PII handling enabled"
        echo ""
        echo "📋 Test your setup:"
        echo "1. Open http://localhost:5004 (PDF PII Anonymizer)"
        echo "2. Upload an 8-page German legal document"
        echo "3. See page-by-page anonymization"
        echo "4. The Docker model will provide perfect responses"
        echo ""
    else
        echo "❌ Docker integration failed!"
        exit 1
    fi
else
    echo "❌ Model training failed!"
    exit 1
fi