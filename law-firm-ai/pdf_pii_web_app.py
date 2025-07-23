#!/usr/bin/env python3
"""
PDF PII Web Application - OCR + PII Anonymization for Scanned PDFs
Handles 8-page German legal documents with OCR processing
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
    flask_available = True
except ImportError:
    flask_available = False

from pdf_ocr_processor import PDFOCRProcessor

# Enhanced HTML template with PDF upload capability
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔒 PDF PII Anonymizer - Law Firm Vision 2030</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .feature-badges {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .badge {
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 30px;
        }
        .input-section, .output-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e9ecef;
        }
        .section-title {
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .upload-area {
            border: 3px dashed #3498db;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: #f8f9fa;
            transition: all 0.3s;
            cursor: pointer;
            margin: 15px 0;
        }
        .upload-area:hover {
            background: #e3f2fd;
            border-color: #2980b9;
        }
        .upload-area.dragover {
            background: #bbdefb;
            border-color: #1976d2;
        }
        .upload-icon {
            font-size: 3em;
            color: #3498db;
            margin-bottom: 15px;
        }
        .file-input {
            display: none;
        }
        .file-info {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
            display: none;
        }
        textarea {
            width: 100%;
            height: 300px;
            padding: 15px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        .btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin: 10px 0;
            width: 100%;
        }
        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
        }
        .btn:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .btn-secondary {
            background: #95a5a6;
            margin: 5px;
            padding: 10px 15px;
            font-size: 14px;
            width: auto;
        }
        .processing-status {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        .processing-status.success {
            background: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        .processing-status.error {
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-number { font-size: 1.8em; font-weight: bold; color: #3498db; }
        .stat-label { font-size: 0.8em; color: #7f8c8d; margin-top: 5px; }
        .entities-list {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            max-height: 200px;
            overflow-y: auto;
        }
        .entity-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin: 5px 0;
            background: #f1f3f4;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #3498db, #2980b9);
            width: 0%;
            transition: width 0.3s;
        }
        .tabs {
            display: flex;
            background: #f1f3f4;
            border-radius: 8px;
            margin: 15px 0;
        }
        .tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            border-radius: 6px;
            transition: background 0.2s;
        }
        .tab.active {
            background: #3498db;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .page-nav {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 2px solid #e9ecef;
        }
        .page-btn {
            padding: 8px 15px;
            border: 2px solid #3498db;
            background: white;
            color: #3498db;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
            min-width: 80px;
            text-align: center;
        }
        .page-btn:hover {
            background: #e3f2fd;
        }
        .page-btn.active {
            background: #3498db;
            color: white;
        }
        .page-btn.has-pii {
            border-color: #e74c3c;
            color: #e74c3c;
        }
        .page-btn.has-pii.active {
            background: #e74c3c;
            color: white;
        }
        .page-viewer {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            border: 2px solid #e9ecef;
        }
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f1f3f4;
        }
        .page-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }
        .page-stats {
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #7f8c8d;
        }
        .page-text-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 15px 0;
        }
        .page-text-section {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 15px;
        }
        .page-text-section h4 {
            margin-bottom: 10px;
            color: #2c3e50;
        }
        .page-text {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        .page-entities {
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .page-entity-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 10px;
            margin: 3px 0;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #3498db;
            font-size: 0.9em;
        }
        .download-options {
            display: flex;
            gap: 10px;
            margin: 15px 0;
        }
        .download-btn {
            background: #27ae60;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        .download-btn:hover {
            background: #219a52;
        }
        @media (max-width: 768px) {
            .main-content { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
            .feature-badges { flex-direction: column; align-items: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 PDF PII Anonymizer</h1>
            <p>OCR + Real-time German Legal Document Processing</p>
            <div class="feature-badges">
                <div class="badge">📄 8-Page PDF Support</div>
                <div class="badge">🔍 OCR Processing</div>
                <div class="badge">🇩🇪 German Language</div>
                <div class="badge">⚡ Real-time Results</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="input-section">
                <div class="section-title">
                    📤 Upload PDF Document
                </div>
                
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('upload')">📄 PDF Upload</div>
                    <div class="tab" onclick="switchTab('text')">📝 Text Input</div>
                </div>
                
                <div id="uploadTab" class="tab-content active">
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <div class="upload-icon">📄</div>
                        <h3>Drop PDF here or click to upload</h3>
                        <p>Supports scanned PDFs up to 8 pages</p>
                        <p style="font-size: 0.9em; color: #7f8c8d; margin-top: 10px;">
                            Accepts .pdf files only
                        </p>
                    </div>
                    <input type="file" id="fileInput" class="file-input" accept=".pdf" onchange="handleFileSelect(event)">
                    
                    <div id="fileInfo" class="file-info">
                        <strong>📄 Selected File:</strong>
                        <div id="fileName"></div>
                        <div id="fileSize"></div>
                    </div>
                    
                    <div id="processingStatus" class="processing-status">
                        <div id="statusText">🔍 Processing PDF...</div>
                        <div class="progress-bar">
                            <div id="progressFill" class="progress-fill"></div>
                        </div>
                    </div>
                    
                    <button class="btn" id="processPdfBtn" onclick="processPDF()" disabled>
                        🔍 Extract Text & Detect PII
                    </button>
                </div>
                
                <div id="textTab" class="tab-content">
                    <textarea id="inputText" placeholder="Or paste your German legal document text here..."></textarea>
                    
                    <div style="display: flex; gap: 10px; margin: 15px 0;">
                        <button class="btn btn-secondary" onclick="loadExample()">📄 Load Example</button>
                        <button class="btn btn-secondary" onclick="clearText()">🗑️ Clear</button>
                    </div>
                    
                    <button class="btn" onclick="processText()">🔍 Detect & Anonymize PII</button>
                </div>
            </div>
            
            <div class="output-section">
                <div class="section-title">
                    🔒 Anonymized Result
                </div>
                <textarea id="outputText" readonly placeholder="Anonymized text will appear here..."></textarea>
                
                <div class="stats" id="stats" style="display: none;">
                    <div class="stat-box">
                        <div class="stat-number" id="pagesCount">0</div>
                        <div class="stat-label">Pages</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="entitiesCount">0</div>
                        <div class="stat-label">PII Entities</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="processingTime">0</div>
                        <div class="stat-label">Time (ms)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" id="originalLength">0</div>
                        <div class="stat-label">Characters</div>
                    </div>
                </div>
                
                <div class="entities-list" id="entitiesList" style="display: none;"></div>
                
                <!-- NEW: Individual Page Results -->
                <div id="pageResults" style="display: none;">
                    <div class="section-title">
                        📄 Individual Pages
                    </div>
                    <div id="pageNavigation" class="page-nav"></div>
                    <div id="pageContent" class="page-viewer"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:5004';
        let currentFile = null;
        
        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
        }
        
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file && file.type === 'application/pdf') {
                currentFile = file;
                document.getElementById('fileInfo').style.display = 'block';
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('fileSize').textContent = `Size: ${(file.size / 1024 / 1024).toFixed(2)} MB`;
                document.getElementById('processPdfBtn').disabled = false;
            } else {
                alert('Please select a valid PDF file');
                event.target.value = '';
            }
        }
        
        // Drag and drop functionality
        const uploadArea = document.querySelector('.upload-area');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type === 'application/pdf') {
                document.getElementById('fileInput').files = files;
                handleFileSelect({ target: { files: files } });
            } else {
                alert('Please drop a valid PDF file');
            }
        });
        
        async function processPDF() {
            if (!currentFile) {
                alert('Please select a PDF file first');
                return;
            }
            
            const statusDiv = document.getElementById('processingStatus');
            const statusText = document.getElementById('statusText');
            const progressFill = document.getElementById('progressFill');
            
            // Show processing status
            statusDiv.style.display = 'block';
            statusDiv.className = 'processing-status';
            statusText.textContent = '🔍 Uploading and processing PDF...';
            progressFill.style.width = '20%';
            
            try {
                const formData = new FormData();
                formData.append('file', currentFile);
                
                progressFill.style.width = '50%';
                statusText.textContent = '📖 Extracting text with OCR...';
                
                const response = await fetch(`${API_BASE}/process-pdf`, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                progressFill.style.width = '80%';
                statusText.textContent = '🔍 Detecting PII entities...';
                
                const data = await response.json();
                
                progressFill.style.width = '100%';
                statusText.textContent = '✅ Processing completed successfully!';
                statusDiv.className = 'processing-status success';
                
                // Update output
                document.getElementById('outputText').value = data.anonymized_text;
                
                // Update stats
                document.getElementById('pagesCount').textContent = data.stats.pages;
                document.getElementById('entitiesCount').textContent = data.entities_found;
                document.getElementById('processingTime').textContent = Math.round(data.processing_time * 1000);
                document.getElementById('originalLength').textContent = data.stats.original_length.toLocaleString();
                document.getElementById('stats').style.display = 'grid';
                
                // Update entities list
                updateEntitiesList(data.entity_summary);
                
                // NEW: Display individual page results
                if (data.page_results) {
                    displayPageResults(data.page_results);
                }
                
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 3000);
                
            } catch (error) {
                console.error('Error:', error);
                statusText.textContent = '❌ Error processing PDF: ' + error.message;
                statusDiv.className = 'processing-status error';
                progressFill.style.width = '0%';
            }
        }
        
        function loadExample() {
            const example = `Rechtsanwaltskanzlei Müller & Partner GmbH
Berliner Straße 123
10115 Berlin

Betreff: Rechtssache gegen Hans Schmidt
Aktenzeichen: 4 C 2156/2024
Telefon: +49 30 12345678
E-Mail: info@mueller-partner.de
IBAN: DE89 3704 0044 0532 0130 00

Sehr geehrte Damen und Herren,

hiermit teilen wir Ihnen mit, dass unser Mandant Hans Schmidt, 
wohnhaft in der Hauptstraße 45, 12345 Musterstadt, eine Klage 
gegen Ihre Versicherungsgesellschaft einreichen wird.

Die Schadenshöhe beläuft sich auf 25.000,00 EUR.

Weitere beteiligte Personen:
- Maria Schmidt (Ehefrau des Mandanten)
- Dr. Weber (behandelnder Arzt)  
- Klaus Mustermann (Zeuge)
- Steuer-ID: 12 345 678 901

Mit freundlichen Grüßen
Dr. Andrea Müller
Rechtsanwältin

Kontakt: a.mueller@firma.de
Mobil: 0171 9876543`;
            document.getElementById('inputText').value = example;
        }
        
        function clearText() {
            document.getElementById('inputText').value = '';
            document.getElementById('outputText').value = '';
            document.getElementById('stats').style.display = 'none';
            document.getElementById('entitiesList').style.display = 'none';
        }
        
        async function processText() {
            const inputText = document.getElementById('inputText').value.trim();
            if (!inputText) {
                alert('Please enter some text to process');
                return;
            }
            
            document.getElementById('outputText').value = '🔍 Processing...';
            
            try {
                const response = await fetch(`${API_BASE}/detect-pii`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: inputText })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                document.getElementById('outputText').value = data.anonymized_text;
                document.getElementById('pagesCount').textContent = '1';
                document.getElementById('entitiesCount').textContent = data.entities_found;
                document.getElementById('processingTime').textContent = Math.round(data.processing_time * 1000);
                document.getElementById('originalLength').textContent = data.stats.original_length.toLocaleString();
                document.getElementById('stats').style.display = 'grid';
                
                updateEntitiesList(data.entity_summary);
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('outputText').value = '❌ Error processing text: ' + error.message;
            }
        }
        
        function updateEntitiesList(entitySummary) {
            const entitiesList = document.getElementById('entitiesList');
            if (entitySummary && Object.keys(entitySummary).length > 0) {
                let html = '<h4>🎯 Detected PII Types:</h4>';
                for (const [type, info] of Object.entries(entitySummary)) {
                    html += `
                        <div class="entity-item">
                            <span>${info.icon} ${info.description}</span>
                            <span><strong>${info.count}</strong> found</span>
                        </div>
                    `;
                }
                entitiesList.innerHTML = html;
                entitiesList.style.display = 'block';
            } else {
                entitiesList.innerHTML = '<p>✅ No PII entities detected in the text.</p>';
                entitiesList.style.display = 'block';
            }
        }
        
        // NEW: Page navigation functions
        let currentPageResults = [];
        let currentPageIndex = 0;
        
        function displayPageResults(pageResults) {
            currentPageResults = pageResults;
            
            if (!pageResults || pageResults.length === 0) {
                document.getElementById('pageResults').style.display = 'none';
                return;
            }
            
            // Show page results section
            document.getElementById('pageResults').style.display = 'block';
            
            // Create page navigation
            const pageNav = document.getElementById('pageNavigation');
            let navHtml = '<div style="margin-bottom: 10px;"><strong>📄 Navigate Pages:</strong></div>';
            
            pageResults.forEach((page, index) => {
                const hasPII = page.entity_count > 0;
                const isActive = index === currentPageIndex;
                const classes = `page-btn ${isActive ? 'active' : ''} ${hasPII ? 'has-pii' : ''}`;
                
                navHtml += `
                    <button class="${classes}" onclick="showPage(${index})">
                        Page ${page.page}
                        ${hasPII ? `<br><small>${page.entity_count} PII</small>` : '<br><small>Clean</small>'}
                    </button>
                `;
            });
            
            pageNav.innerHTML = navHtml;
            
            // Show first page by default
            showPage(0);
        }
        
        function showPage(pageIndex) {
            if (!currentPageResults || pageIndex >= currentPageResults.length) return;
            
            currentPageIndex = pageIndex;
            const page = currentPageResults[pageIndex];
            
            // Update navigation buttons
            document.querySelectorAll('.page-btn').forEach((btn, index) => {
                btn.classList.toggle('active', index === pageIndex);
            });
            
            // Display page content
            const pageContent = document.getElementById('pageContent');
            
            let entitiesHtml = '';
            if (page.entities && page.entities.length > 0) {
                entitiesHtml = `
                    <div class="page-entities">
                        <h4>🎯 PII Entities Found on This Page (${page.entities.length}):</h4>
                        ${page.entities.map(entity => `
                            <div class="page-entity-item">
                                <span>"${entity.original}" → ${entity.replacement}</span>
                                <span>${Math.round(entity.confidence * 100)}% confidence</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                entitiesHtml = `
                    <div class="page-entities">
                        <h4>✅ No PII entities found on this page</h4>
                    </div>
                `;
            }
            
            pageContent.innerHTML = `
                <div class="page-header">
                    <div class="page-title">📄 Page ${page.page}</div>
                    <div class="page-stats">
                        <span>📊 ${page.character_count.toLocaleString()} characters</span>
                        <span>🎯 ${page.entity_count} PII entities</span>
                    </div>
                </div>
                
                <div class="page-text-container">
                    <div class="page-text-section">
                        <h4>📝 Original Text</h4>
                        <div class="page-text">${page.original_text || '(Empty page)'}</div>
                    </div>
                    <div class="page-text-section">
                        <h4>🔒 Anonymized Text</h4>
                        <div class="page-text">${page.anonymized_text || '(Empty page)'}</div>
                    </div>
                </div>
                
                ${entitiesHtml}
                
                <div class="download-options">
                    <button class="download-btn" onclick="downloadPage(${pageIndex}, 'original')">
                        📄 Download Original Page ${page.page}
                    </button>
                    <button class="download-btn" onclick="downloadPage(${pageIndex}, 'anonymized')">
                        🔒 Download Anonymized Page ${page.page}
                    </button>
                </div>
            `;
        }
        
        function downloadPage(pageIndex, type) {
            if (!currentPageResults || pageIndex >= currentPageResults.length) return;
            
            const page = currentPageResults[pageIndex];
            const text = type === 'original' ? page.original_text : page.anonymized_text;
            const filename = `page_${page.page}_${type}.txt`;
            
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
"""

def create_pdf_app():
    """Create Flask app with PDF processing capabilities"""
    if not flask_available:
        print("❌ Flask not available")
        return None
    
    app = Flask(__name__)
    CORS(app)
    
    # Initialize PDF processor
    pdf_processor = PDFOCRProcessor()
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "healthy", 
            "service": "PDF PII Anonymizer",
            "ocr_methods": pdf_processor.ocr_methods
        })
    
    @app.route('/process-pdf', methods=['POST'])
    def process_pdf():
        """Process uploaded PDF file"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file uploaded"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({"error": "Only PDF files are supported"}), 400
            
            # Save uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            
            try:
                # Process the PDF
                result = pdf_processor.process_pdf(temp_path)
                
                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify({"error": result.get('error', 'PDF processing failed')}), 500
                    
            finally:
                # Clean up temp file
                try:
                    os.remove(temp_path)
                    os.rmdir(temp_dir)
                except:
                    pass
        
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/detect-pii', methods=['POST'])
    def detect_pii():
        """Detect PII in text (fallback for text input)"""
        try:
            if request.is_json:
                data = request.get_json()
                text = data.get('text', '')
            else:
                text = request.form.get('text', '')
            
            if not text or len(text.strip()) < 5:
                return jsonify({"error": "No text provided or text too short"}), 400
            
            start_time = datetime.now()
            
            # Use the PDF processor's PII detection
            entities = pdf_processor.detect_pii(text)
            anonymized_text = pdf_processor.anonymize_text(text, entities)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare entity summary
            entity_summary = {}
            for entity in entities:
                entity_type = entity['type']
                if entity_type not in entity_summary:
                    pattern_info = pdf_processor.patterns[entity_type]
                    desc_parts = pattern_info['description'].split(' ', 1)
                    icon = desc_parts[0] if desc_parts[0] in '👤📞📧💳📮📁🆔💰🏠' else '🔍'
                    description = desc_parts[1] if len(desc_parts) > 1 else pattern_info['description']
                    
                    entity_summary[entity_type] = {
                        'count': 0,
                        'description': description,
                        'icon': icon
                    }
                entity_summary[entity_type]['count'] += 1
            
            return jsonify({
                "success": True,
                "original_text": text,
                "anonymized_text": anonymized_text,
                "processing_time": round(processing_time, 3),
                "entities_found": len(entities),
                "entity_summary": entity_summary,
                "detailed_entities": entities,
                "stats": {
                    "original_length": len(text),
                    "anonymized_length": len(anonymized_text),
                    "pages": 1
                }
            })
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    
    return app

def main():
    """Main function to run the PDF PII web app"""
    print("🔒 PDF PII Anonymizer with OCR Support")
    print("=" * 60)
    
    # Try to create Flask app
    app = create_pdf_app()
    if app is None:
        print("❌ Cannot create web app - Flask not available")
        return
    
    print("🚀 Starting PDF PII Anonymizer Service")
    print("📍 URL: http://localhost:5004")
    print("💡 Open the URL in your browser to upload PDFs")
    print("✨ Features:")
    print("   • 📄 8-page PDF document support")
    print("   • 🔍 OCR for scanned documents")
    print("   • 🇩🇪 German language processing")
    print("   • ⚡ Real-time PII detection")
    print("   • 📊 Visual progress tracking")
    print("   • 🎯 Detailed statistics")
    print("")
    
    try:
        app.run(host='0.0.0.0', port=5004, debug=False)
    except KeyboardInterrupt:
        print("\n👋 PDF PII Anonymizer stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main()