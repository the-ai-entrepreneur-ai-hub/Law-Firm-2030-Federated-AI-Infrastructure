document.addEventListener('DOMContentLoaded', () => {
    // --- INTELLIGENT API ENDPOINTS ---
    const apiUrl = 'http://localhost:5001/process-document'; // Legacy endpoint
    const intelligentApiUrl = 'http://localhost:5001/api/generate'; // New intelligent API
    const feedbackApiUrl = 'http://localhost:5001/api/feedback'; // Feedback API
    const metricsApiUrl = 'http://localhost:5001/api/metrics'; // Metrics API 

    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name-display');
    const statusMessage = document.getElementById('status-message');
    const submitButton = document.getElementById('submit-button');
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    const copyButton = document.getElementById('copy-results');
    const copyAllButton = document.getElementById('copy-all-data');
    const newDocumentButton = document.getElementById('new-document');
    
    // Process detail elements
    const piiStats = document.getElementById('pii-stats');
    const piiSamples = document.getElementById('pii-samples');
    const processStats = document.getElementById('process-stats');
    const anonymizedContent = document.getElementById('anonymized-content');
    const originalContent = document.getElementById('original-content');
    
    // Store complete data for copying and feedback
    let completeData = null;
    let currentDocumentId = null;
    let currentModelResponse = null;

    // Update file name display when a file is chosen
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = `Selected: ${fileInput.files[0].name}`;
        } else {
            fileNameDisplay.textContent = '';
        }
    });

    // Handle the form submission
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Stop the browser from navigating away

        if (fileInput.files.length === 0) {
            showStatus('Please choose a file first.', 'error');
            return;
        }

        const file = fileInput.files[0];
        
        // Validate file type - now includes text files for German legal documents
        const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'text/plain'];
        if (!allowedTypes.includes(file.type)) {
            showStatus('Please select a valid PDF, PNG, JPG, or TXT file.', 'error');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showStatus('File size must be less than 10MB.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file); 

        // --- Provide user feedback ---
        showStatus('Uploading and processing document...', 'loading');
        submitButton.disabled = true;
        submitButton.querySelector('.button-text').textContent = 'Processing...';

        try {
            // Always use the intelligent API - no fallback to legacy
            const extractedText = await extractTextFromFile(file);
            const documentType = detectDocumentType(extractedText);
            
            showStatus('📝 Dokument wird bearbeitet...', 'loading');
            
            // Call intelligent API for document generation
            const intelligentResponse = await fetch(intelligentApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: extractedText,
                    document_type: documentType,
                    user_id: 'user_' + Date.now()
                }),
            });

            if (!intelligentResponse.ok) {
                throw new Error(`API error: ${intelligentResponse.status}`);
            }
            
            const intelligentResult = await intelligentResponse.json();
            
            if (!intelligentResult.success) {
                throw new Error(intelligentResult.error || 'API returned unsuccessful response');
            }
            
            currentDocumentId = intelligentResult.document_id;
            currentModelResponse = intelligentResult;
            
            // Show intelligent response
            showIntelligentResults(intelligentResult, extractedText);

        } catch (error) {
            console.error('Upload Error:', error);
            showStatus(`❌ Error: ${error.message}`, 'error');
        } finally {
            // --- Reset the button ---
            submitButton.disabled = false;
            submitButton.querySelector('.button-text').textContent = 'Upload & Process';
        }
    });

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status status-${type}`; // Add a base class for styling
        statusMessage.style.display = 'block';
    }

    async function extractTextFromFile(file) {
        """Extract text content from uploaded file"""
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            if (file.type === 'text/plain') {
                reader.onload = (e) => resolve(e.target.result);
                reader.readAsText(file);
            } else if (file.type === 'application/pdf') {
                // For PDFs, we'll need to process server-side
                resolve(`[PDF FILE: ${file.name}] - Content will be extracted server-side`);
            } else {
                // For images, indicate OCR processing needed
                resolve(`[IMAGE FILE: ${file.name}] - OCR processing will be performed server-side`);
            }
        });
    }

    function detectDocumentType(text) {
        """Detect document type from text content"""
        const textLower = text.toLowerCase();
        
        if (textLower.includes('mahnung') || textLower.includes('zahlungserinnerung')) {
            return 'mahnung';
        } else if (textLower.includes('klage') || textLower.includes('klageschrift')) {
            return 'klage';
        } else if (textLower.includes('kündigung')) {
            return 'kuendigung';
        } else if (textLower.includes('vertrag') || textLower.includes('vereinbarung')) {
            return 'contract';
        } else if (textLower.includes('nda') || textLower.includes('geheimhaltung')) {
            return 'nda';
        } else {
            return 'general';
        }
    }

    function showIntelligentResults(result, originalText) {
        """Show results from intelligent API"""
        completeData = {
            ...result,
            original_text: originalText,
            processing_type: 'intelligent'
        };
        
        // Populate main response area - ONLY show the legal response content
        resultsContent.innerHTML = `
            <div class="legal-response">
                <div class="response-content">
                    ${formatLegalResponse(result.response)}
                </div>
            </div>
        `;
        
        // Populate simple processing statistics without AI mentions
        populateLegalProcessStats(result);
        
        // Show original and processed content
        originalContent.textContent = originalText;
        anonymizedContent.innerHTML = `
            <div class="legal-document">
                <h4>Rechtliche Antwort:</h4>
                <div class="response-text">${result.response}</div>
            </div>
        `;
        
        // Add feedback buttons
        addFeedbackButtons();
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function populateLegalProcessStats(result) {
        """Populate statistics for legal processing"""
        const statsHTML = `
            <div class="stat-card">
                <span class="stat-value">${result.processing_time.toFixed(2)}s</span>
                <span class="stat-label">Bearbeitungszeit</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">✓</span>
                <span class="stat-label">Dokument verarbeitet</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">🏛️</span>
                <span class="stat-label">Rechtliche Prüfung</span>
            </div>
        `;
        processStats.innerHTML = statsHTML;
    }

    function getConfidenceClass(confidence) {
        """Get CSS class for confidence level"""
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.6) return 'medium';
        return 'low';
    }

    function formatLegalResponse(response) {
        """Format legal response for better display"""
        return response
            .replace(/\n\n/g, '</p><p>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    function addFeedbackButtons() {
        """Add feedback buttons for quality assurance"""
        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'feedback-container';
        feedbackContainer.innerHTML = `
            <div class="feedback-section">
                <h4>💭 Qualitätsbewertung</h4>
                <p>Helfen Sie uns, unseren Service zu verbessern:</p>
                <div class="feedback-buttons">
                    <button class="feedback-btn accept" onclick="submitFeedback('accept')">
                        ✅ Gut - Antwort akzeptieren
                    </button>
                    <button class="feedback-btn reject" onclick="submitFeedback('reject')">
                        ❌ Schlecht - Antwort ablehnen
                    </button>
                    <button class="feedback-btn improve" onclick="showImprovementEditor()">
                        ✏️ Verbessern - Antwort bearbeiten
                    </button>
                </div>
                <div class="improvement-editor" id="improvement-editor" style="display: none;">
                    <h5>Verbesserte Antwort:</h5>
                    <textarea id="improved-response" rows="8" placeholder="Geben Sie hier Ihre verbesserte Version ein..."></textarea>
                    <div class="editor-buttons">
                        <button onclick="submitImprovement()" class="btn-primary">Verbesserung senden</button>
                        <button onclick="cancelImprovement()" class="btn-secondary">Abbrechen</button>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(feedbackContainer);
    }

    function showResults(result) {
        // Store complete data
        completeData = result;
        
        // Populate final analysis (now using English translation)
        const analysisText = result.final_response.llm_analysis_english || result.final_response || 'No analysis available';
        const formattedText = formatAnalysisText(analysisText);
        resultsContent.textContent = formattedText;
        
        // Populate process statistics
        if (result.processing_stats) {
            populateProcessStats(result.processing_stats);
        }
        
        // Populate PII details using new format
        if (result.final_response.detected_pii_entities) {
            populatePIIDetails({
                entities_found: result.processing_stats.entities_found || 0,
                entity_types: [...new Set(result.final_response.detected_pii_entities.map(e => e.type))],
                sample_entities: groupPIIEntities(result.final_response.detected_pii_entities),
                entity_breakdown: getEntityBreakdown(result.final_response.detected_pii_entities)
            });
        }
        
        // Populate text content with translations
        originalContent.textContent = result.final_response.original_text_preview || 'No original text available';
        anonymizedContent.textContent = result.final_response.anonymized_text_english || 'No anonymized text available';
        
        // Show results container
        resultsContainer.style.display = 'block';
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function populateProcessStats(stats) {
        const statsHTML = `
            <div class="stat-card">
                <span class="stat-value">${stats.timing.total_time.toFixed(2)}s</span>
                <span class="stat-label">Total Time</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.timing.ocr_time?.toFixed(2) || '0.00'}s</span>
                <span class="stat-label">Text Processing</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.timing.llm_time?.toFixed(2) || '0.00'}s</span>
                <span class="stat-label">AI Analysis Time</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.timing.translation_time?.toFixed(2) || '0.00'}s</span>
                <span class="stat-label">Translation Time</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.entities_found}</span>
                <span class="stat-label">PII Items Found</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.file_size_mb} MB</span>
                <span class="stat-label">File Size</span>
            </div>
        `;
        processStats.innerHTML = statsHTML;
    }

    function populatePIIDetails(piiDetails) {
        // PII Statistics
        const statsHTML = `
            <div class="stat-card">
                <span class="stat-value">${piiDetails.entities_found}</span>
                <span class="stat-label">Total PII Items</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${piiDetails.entity_types.length}</span>
                <span class="stat-label">PII Types Found</span>
            </div>
        `;
        piiStats.innerHTML = statsHTML;
        
        // PII Samples
        let samplesHTML = '';
        for (const [entityType, samples] of Object.entries(piiDetails.sample_entities)) {
            const count = piiDetails.entity_breakdown[entityType] || 0;
            samplesHTML += `
                <div class="pii-type">
                    <div class="pii-type-header">
                        <span>${getEntityTypeLabel(entityType)}</span>
                        <span class="pii-count">${count} found</span>
                    </div>
                    <div class="pii-samples-list">
                        ${samples.map(sample => `
                            <div class="pii-sample">
                                <span class="pii-placeholder">${sample.placeholder}</span>
                                <span class="pii-original">"${sample.original}"</span>
                            </div>
                        `).join('')}
                        ${count > samples.length ? `<div style="text-align: center; color: #64748b; font-style: italic; margin-top: 10px;">... and ${count - samples.length} more</div>` : ''}
                    </div>
                </div>
            `;
        }
        piiSamples.innerHTML = samplesHTML;
    }

    // Helper functions for processing new API format
    function groupPIIEntities(entities) {
        const grouped = {};
        entities.forEach(entity => {
            if (!grouped[entity.type]) {
                grouped[entity.type] = [];
            }
            // Limit to 3 samples per type for display
            if (grouped[entity.type].length < 3) {
                grouped[entity.type].push({
                    placeholder: `[${entity.type}_${grouped[entity.type].length + 1}]`,
                    original: entity.original_text
                });
            }
        });
        return grouped;
    }
    
    function getEntityBreakdown(entities) {
        const breakdown = {};
        entities.forEach(entity => {
            breakdown[entity.type] = (breakdown[entity.type] || 0) + 1;
        });
        return breakdown;
    }
    
    function showHighRiskResults(result) {
        // Show partial results for high-risk documents
        completeData = result;
        
        // Show risk information instead of full analysis
        resultsContent.innerHTML = `
            <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h4 style="color: #856404; margin: 0 0 10px 0;">⚠️ Document Requires Manual Review</h4>
                <p><strong>Risk Score:</strong> ${result.risk_assessment.total_risk_score}</p>
                <p><strong>Risk Factors:</strong></p>
                <ul>
                    ${result.risk_assessment.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                </ul>
                <p><strong>Quasi-identifiers Found:</strong></p>
                <ul>
                    ${result.risk_assessment.quasi_identifiers.map(qi => `<li>${qi}</li>`).join('')}
                </ul>
            </div>
            <p>This document contains too much personally identifiable information to process automatically. Please review manually before processing.</p>
        `;
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function getEntityTypeLabel(entityType) {
        const labels = {
            'PER': '👤 Person Names',
            'ORG': '🏢 Organizations',
            'LOC': '📍 Locations',
            'MISC': '🔤 Miscellaneous',
            'BIC': '🏦 Bank Codes',
            'IBAN': '💳 Bank Accounts',
            'PLZ': '📮 Postal Codes',
            'TELEFON': '📞 Phone Numbers',
            'EMAIL': '📧 Email Addresses',
            'WEBSITE': '🌐 Websites',
            'AKTENZEICHEN': '📁 Case Numbers',
            'GEBURTSDATUM': '🎂 Birth Dates',
            'KENNZEICHEN': '🚗 License Plates'
        };
        return labels[entityType] || `🔸 ${entityType}`;
    }

    function formatAnalysisText(text) {
        // Clean up the text formatting for better display
        return text
            .replace(/\*\*(.*?)\*\*/g, '$1') // Remove markdown bold
            .replace(/^\s+|\s+$/g, '') // Trim whitespace
            .replace(/\n{3,}/g, '\n\n'); // Reduce excessive line breaks
    }

    function hideResults() {
        resultsContainer.style.display = 'none';
    }

    // Copy results to clipboard
    copyButton.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(resultsContent.textContent);
            copyButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                Copied!
            `;
            setTimeout(() => {
                copyButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    Copy Analysis
                `;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showStatus('❌ Failed to copy to clipboard', 'error');
        }
    });

    // Copy all data to clipboard
    copyAllButton.addEventListener('click', async () => {
        if (!completeData) return;
        
        try {
            const allData = JSON.stringify(completeData, null, 2);
            await navigator.clipboard.writeText(allData);
            copyAllButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                Copied!
            `;
            setTimeout(() => {
                copyAllButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
                    Copy All Data
                `;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy all data: ', err);
            showStatus('❌ Failed to copy to clipboard', 'error');
        }
    });

    // Tab functionality
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-button')) {
            // Remove active from all tabs and content
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Add active to clicked tab and corresponding content
            e.target.classList.add('active');
            const tabName = e.target.getAttribute('data-tab');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        }
    });

    // Reset form for new document
    newDocumentButton.addEventListener('click', () => {
        // Reset form
        form.reset();
        fileNameDisplay.textContent = '';
        
        // Hide results and status
        hideResults();
        statusMessage.style.display = 'none';
        
        // Reset to first tab
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.querySelector('.tab-button[data-tab="analysis"]').classList.add('active');
        document.getElementById('tab-analysis').classList.add('active');
        
        // Clear stored data
        completeData = null;
        
        // Scroll back to top
        document.querySelector('.container').scrollIntoView({ behavior: 'smooth' });
    });
});

// Global feedback functions (need to be outside DOMContentLoaded for onclick handlers)
async function submitFeedback(feedbackType) {
    """Submit feedback to the intelligent training system"""
    if (!currentDocumentId) {
        showStatus('❌ No document ID available for feedback', 'error');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5001/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                document_id: currentDocumentId,
                feedback_type: feedbackType,
                user_id: 'user_' + Date.now()
            }),
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus(`✅ Feedback "${feedbackType}" wurde erfolgreich übermittelt!`, 'success');
            
            // Disable feedback buttons after submission
            disableFeedbackButtons();
            
            // Show quality improvement status if triggered
            if (result.training_triggered) {
                showStatus('🔄 Qualitätsverbesserung wird verarbeitet...', 'loading');
            }
        } else {
            throw new Error(result.error || 'Feedback submission failed');
        }
        
    } catch (error) {
        console.error('Feedback error:', error);
        showStatus(`❌ Feedback-Fehler: ${error.message}`, 'error');
    }
}

function showImprovementEditor() {
    """Show the improvement editor"""
    const editor = document.getElementById('improvement-editor');
    const textarea = document.getElementById('improved-response');
    
    // Pre-fill with current response for editing
    if (currentModelResponse && currentModelResponse.response) {
        textarea.value = currentModelResponse.response;
    }
    
    editor.style.display = 'block';
    textarea.focus();
}

async function submitImprovement() {
    """Submit improved response"""
    const improvedText = document.getElementById('improved-response').value.trim();
    
    if (!improvedText) {
        alert('Bitte geben Sie eine verbesserte Version ein.');
        return;
    }
    
    if (!currentDocumentId) {
        showStatus('❌ No document ID available for improvement', 'error');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:5001/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                document_id: currentDocumentId,
                feedback_type: 'improve',
                user_edit: improvedText,
                user_id: 'user_' + Date.now()
            }),
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('✅ Verbesserung wurde erfolgreich übermittelt!', 'success');
            
            // Update display with improved version
            updateResponseDisplay(improvedText);
            
            // Hide editor and disable feedback buttons
            cancelImprovement();
            disableFeedbackButtons();
            
        } else {
            throw new Error(result.error || 'Improvement submission failed');
        }
        
    } catch (error) {
        console.error('Improvement error:', error);
        showStatus(`❌ Verbesserungs-Fehler: ${error.message}`, 'error');
    }
}

function cancelImprovement() {
    """Cancel improvement editing"""
    const editor = document.getElementById('improvement-editor');
    const textarea = document.getElementById('improved-response');
    
    editor.style.display = 'none';
    textarea.value = '';
}

function updateResponseDisplay(improvedText) {
    """Update the response display with improved text"""
    const responseContent = document.querySelector('.response-content');
    if (responseContent) {
        responseContent.innerHTML = `
            <div class="improved-response">
                <div class="improvement-badge">✏️ Verbesserte Version</div>
                ${formatLegalResponse(improvedText)}
            </div>
        `;
    }
    
    // Update anonymized content tab as well
    const anonymizedContent = document.getElementById('anonymized-content');
    if (anonymizedContent) {
        anonymizedContent.innerHTML = `
            <div class="generated-response">
                <h4>✏️ Verbesserte rechtliche Antwort:</h4>
                <div class="response-text improved">${improvedText}</div>
            </div>
        `;
    }
}

function disableFeedbackButtons() {
    """Disable feedback buttons after submission"""
    const feedbackButtons = document.querySelectorAll('.feedback-btn');
    feedbackButtons.forEach(button => {
        button.disabled = true;
        button.style.opacity = '0.5';
        button.style.cursor = 'not-allowed';
    });
    
    // Add feedback submitted message
    const feedbackSection = document.querySelector('.feedback-section');
    if (feedbackSection) {
        const submittedMessage = document.createElement('div');
        submittedMessage.className = 'feedback-submitted';
        submittedMessage.innerHTML = '<p>✅ <strong>Feedback wurde übermittelt.</strong> Vielen Dank für Ihr Feedback zur Verbesserung unseres Services!</p>';
        feedbackSection.appendChild(submittedMessage);
    }
}

function formatLegalResponse(response) {
    """Format legal response for better display"""
    return response
        .replace(/\n\n/g, '</p><p>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function showStatus(message, type) {
    """Show status message"""
    const statusMessage = document.getElementById('status-message');
    if (statusMessage) {
        statusMessage.textContent = message;
        statusMessage.className = `status status-${type}`;
        statusMessage.style.display = 'block';
    }
}