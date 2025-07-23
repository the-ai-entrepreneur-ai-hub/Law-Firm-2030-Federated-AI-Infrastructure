#!/bin/bash
echo "🔒 Migrating to Zero-Trust Sanitization Architecture"
echo "=================================================="
echo ""

# Set working directory
cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai"

# Stop current container
echo "1. Stopping current sanitizer..."
docker-compose stop sanitizer

# Backup current system
echo "2. Backing up current system..."
cp sanitizer_app.py sanitizer_app.py.backup.$(date +%Y%m%d_%H%M%S)
echo "   ✓ Backup created"

# Build new zero-trust container
echo "3. Building zero-trust sanitizer container..."
docker-compose build --no-cache sanitizer

# Start new system
echo "4. Starting zero-trust sanitizer..."
docker-compose up -d sanitizer

# Wait for startup
echo "5. Waiting for system startup..."
sleep 10

# Health check
echo "6. Performing health check..."
if curl -f -s http://localhost:5001/health > /dev/null; then
    echo "   ✅ Zero-trust sanitizer is healthy!"
    echo ""
    echo "🎉 MIGRATION SUCCESSFUL!"
    echo ""
    echo "New Features Available:"
    echo "• Parallel PII detection (NER + Regex + Fuzzy + Contextual)"
    echo "• Visual PII sanitization (faces, signatures, stamps)"
    echo "• Risk-based human-in-the-loop triage"
    echo "• PII-scrubbing secure logging"
    echo "• Consolidated redaction pipeline"
    echo "• Zero-trust architecture"
    echo ""
    echo "🚨 SECURITY IMPROVEMENTS:"
    echo "• No more debug data leakage"
    echo "• All logging is PII-scrubbed"
    echo "• Environment-based configuration"
    echo "• Non-root container execution"
else
    echo "   ❌ Health check failed!"
    echo "   Rolling back to previous version..."
    
    # Rollback
    docker-compose stop sanitizer
    cp sanitizer_app.py.backup.* sanitizer_app.py 2>/dev/null || echo "No backup found"
    docker-compose up -d sanitizer
    
    echo "   ⚠️  Rollback completed. Please check logs for errors."
fi

echo ""
echo "📊 To view real-time logs:"
echo "./view-logs.sh"