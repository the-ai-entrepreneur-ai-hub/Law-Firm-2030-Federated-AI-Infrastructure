document.addEventListener('DOMContentLoaded', () => {
    // --- DIRECT API ENDPOINT (bypassing n8n webhook issues) ---
    const apiUrl = 'http://localhost:5001/process-document'; 

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
    
    // Store complete data for copying
    let completeData = null;

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
            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }
            
            if (result.success && result.final_response) {
                showStatus('✅ Document processed and translated successfully!', 'success');
                showResults(result);
                console.log('Processing result:', result);
            } else if (result.requires_human_review) {
                showStatus(`⚠️ Document requires human review. Risk score: ${result.risk_assessment.total_risk_score}`, 'warning');
                showHighRiskResults(result);
            } else {
                throw new Error(result.error || result.message || 'An unknown error occurred in the response.');
            }

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