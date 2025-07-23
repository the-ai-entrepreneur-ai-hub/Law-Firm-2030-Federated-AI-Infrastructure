#!/bin/bash
echo "📊 Starting real-time Docker logs for Law Firm Sanitizer..."
echo "======================================================"
echo "Press Ctrl+C to stop viewing logs"
echo ""

cd "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai"
docker-compose logs -f --tail=20 sanitizer