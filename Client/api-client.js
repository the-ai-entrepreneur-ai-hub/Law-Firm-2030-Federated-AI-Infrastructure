/**
 * AnwaltsAI API Client
 * Handles all backend communication with proper error handling and authentication
 */
class AnwaltsAIApiClient {
    constructor(baseUrl = 'http://localhost:5001') {
        this.baseUrl = baseUrl;
        this.authToken = localStorage.getItem('anwalts_auth_token');
    }

    // =========================
    // AUTHENTICATION ENDPOINTS
    // =========================
    
    async login(email, password) {
        try {
            const response = await this.post('/auth/login', {
                email,
                password
            });
            
            if (response.success && response.token) {
                this.authToken = response.token;
                localStorage.setItem('anwalts_auth_token', response.token);
                localStorage.setItem('anwalts_user', JSON.stringify(response.user));
            }
            
            return response;
        } catch (error) {
            console.error('Login error:', error);
            throw new Error('Anmeldung fehlgeschlagen');
        }
    }
    
    async logout() {
        try {
            await this.post('/auth/logout');
        } catch (error) {
            console.warn('Logout warning:', error);
        } finally {
            this.authToken = null;
            localStorage.removeItem('anwalts_auth_token');
            localStorage.removeItem('anwalts_user');
        }
    }
    
    async validateToken() {
        try {
            const response = await this.get('/auth/validate');
            return response.valid;
        } catch (error) {
            return false;
        }
    }

    // =========================
    // DOCUMENT GENERATION ENDPOINTS
    // =========================
    
    async generateDocument(prompt, templateId = null, uploadedFile = null) {
        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            
            if (templateId) {
                formData.append('template_id', templateId);
            }
            
            if (uploadedFile) {
                formData.append('file', uploadedFile);
            }
            
            const response = await this.postFormData('/generate-document', formData);
            return response;
        } catch (error) {
            console.error('Document generation error:', error);
            throw new Error('Dokumentenerstellung fehlgeschlagen');
        }
    }
    
    async processDocument(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await this.postFormData('/process-document', formData);
            return response;
        } catch (error) {
            console.error('Document processing error:', error);
            throw new Error('Dokumentenverarbeitung fehlgeschlagen');
        }
    }
    
    async provideFeedback(documentId, feedbackType, userEdit = null, comment = null) {
        try {
            const response = await this.post('/feedback', {
                document_id: documentId,
                feedback_type: feedbackType, // 'accept', 'reject', 'improve'
                user_edit: userEdit,
                comment: comment
            });
            return response;
        } catch (error) {
            console.error('Feedback error:', error);
            throw new Error('Feedback konnte nicht übermittelt werden');
        }
    }

    // =========================
    // EMAIL MANAGEMENT ENDPOINTS
    // =========================
    
    async getEmails(filter = 'all', page = 1, limit = 50) {
        try {
            const response = await this.get(`/emails?filter=${filter}&page=${page}&limit=${limit}`);
            return response;
        } catch (error) {
            console.error('Email fetch error:', error);
            throw new Error('E-Mails konnten nicht geladen werden');
        }
    }
    
    async getEmail(emailId) {
        try {
            const response = await this.get(`/emails/${emailId}`);
            return response;
        } catch (error) {
            console.error('Email detail error:', error);
            throw new Error('E-Mail-Details konnten nicht geladen werden');
        }
    }
    
    async generateEmailResponse(emailId, prompt = null) {
        try {
            const response = await this.post(`/emails/${emailId}/generate-response`, {
                prompt: prompt
            });
            return response;
        } catch (error) {
            console.error('Email response generation error:', error);
            throw new Error('E-Mail-Antwort konnte nicht generiert werden');
        }
    }

    // =========================
    // TEMPLATE MANAGEMENT ENDPOINTS
    // =========================
    
    async getTemplates(category = 'all', type = 'all') {
        try {
            const response = await this.get(`/templates?category=${category}&type=${type}`);
            return response;
        } catch (error) {
            console.error('Templates fetch error:', error);
            throw new Error('Vorlagen konnten nicht geladen werden');
        }
    }
    
    async getTemplate(templateId) {
        try {
            const response = await this.get(`/templates/${templateId}`);
            return response;
        } catch (error) {
            console.error('Template detail error:', error);
            throw new Error('Vorlage konnte nicht geladen werden');
        }
    }
    
    async saveTemplate(name, content, category, type = 'personal') {
        try {
            const response = await this.post('/templates', {
                name,
                content,
                category,
                type
            });
            return response;
        } catch (error) {
            console.error('Template save error:', error);
            throw new Error('Vorlage konnte nicht gespeichert werden');
        }
    }
    
    async updateTemplate(templateId, updates) {
        try {
            const response = await this.put(`/templates/${templateId}`, updates);
            return response;
        } catch (error) {
            console.error('Template update error:', error);
            throw new Error('Vorlage konnte nicht aktualisiert werden');
        }
    }
    
    async deleteTemplate(templateId) {
        try {
            const response = await this.delete(`/templates/${templateId}`);
            return response;
        } catch (error) {
            console.error('Template delete error:', error);
            throw new Error('Vorlage konnte nicht gelöscht werden');
        }
    }

    // =========================
    // ANALYTICS & DASHBOARD ENDPOINTS
    // =========================
    
    async getDashboardStats() {
        try {
            const response = await this.get('/dashboard/stats');
            return response;
        } catch (error) {
            console.error('Dashboard stats error:', error);
            return {
                documents_created: 0,
                emails_processed: 0,
                templates_saved: 0,
                recent_activity: []
            };
        }
    }
    
    async getRecentActivity(limit = 10) {
        try {
            const response = await this.get(`/dashboard/recent-activity?limit=${limit}`);
            return response.activities || [];
        } catch (error) {
            console.error('Recent activity error:', error);
            // Return mock data for now
            return [
                {
                    id: 1,
                    type: 'document',
                    title: 'Kaufvertrag erstellt',
                    date: new Date().toISOString(),
                    status: 'Abgeschlossen'
                },
                {
                    id: 2,
                    type: 'email',
                    title: 'E-Mail an Mandant beantwortet',
                    date: new Date(Date.now() - 86400000).toISOString(),
                    status: 'Gesendet'
                },
                {
                    id: 3,
                    type: 'template',
                    title: 'Neue Vorlage gespeichert',
                    date: new Date(Date.now() - 172800000).toISOString(),
                    status: 'Aktiv'
                }
            ];
        }
    }
    
    // =========================
    // HEALTH CHECK ENDPOINT
    // =========================
    
    async healthCheck() {
        try {
            const response = await this.get(`/dashboard/activity?limit=${limit}`);
            return response;
        } catch (error) {
            console.error('Recent activity error:', error);
            return { activities: [] };
        }
    }

    // =========================
    // HTTP CLIENT METHODS
    // =========================
    
    async get(endpoint) {
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'GET',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }
    
    async post(endpoint, data) {
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }
    
    async postFormData(endpoint, formData) {
        const headers = this.getHeaders();
        delete headers['Content-Type']; // Let browser set it for FormData
        
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'POST',
            headers: headers,
            body: formData
        });
        return this.handleResponse(response);
    }
    
    async put(endpoint, data) {
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }
    
    async delete(endpoint) {
        const response = await fetch(this.baseUrl + endpoint, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }
    
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }
    
    async handleResponse(response) {
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                this.logout();
                throw new Error('Sitzung abgelaufen. Bitte melden Sie sich erneut an.');
            }
            
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP Error: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    }

    // =========================
    // HEALTH CHECK & CONNECTIVITY
    // =========================
    
    async healthCheck() {
        try {
            const response = await fetch(this.baseUrl + '/health');
            return response.ok;
        } catch (error) {
            return false;
        }
    }
    
    async testConnection() {
        const isHealthy = await this.healthCheck();
        return {
            connected: isHealthy,
            baseUrl: this.baseUrl,
            timestamp: new Date().toISOString()
        };
    }
}

// =========================
// MOCK DATA FOR DEVELOPMENT
// =========================

class MockApiClient extends AnwaltsAIApiClient {
    constructor() {
        super();
        this.mockData = {
            templates: [
                {
                    id: 'sys_001',
                    name: 'Mahnung (1. Stufe)',
                    category: 'payment',
                    type: 'system',
                    content: 'Sehr geehrte Damen und Herren...',
                    usage_count: 45,
                    created_at: '2024-01-15T10:00:00Z'
                },
                {
                    id: 'sys_002', 
                    name: 'Geheimhaltungsvereinbarung',
                    category: 'contracts',
                    type: 'system',
                    content: 'Zwischen den Parteien...',
                    usage_count: 23,
                    created_at: '2024-01-20T14:30:00Z'
                },
                {
                    id: 'pers_001',
                    name: 'Kaufvertrag Immobilie',
                    category: 'contracts',
                    type: 'personal',
                    content: 'Kaufvertrag über eine Immobilie...',
                    usage_count: 12,
                    created_at: '2024-02-01T09:15:00Z'
                }
            ],
            emails: [
                {
                    id: 'email_001',
                    from: 'client@example.com',
                    subject: 'Anfrage Kaufvertrag',
                    date: '2024-01-30T14:20:00Z',
                    preview: 'Sehr geehrte Damen und Herren, ich benötige...',
                    has_attachment: true,
                    status: 'unread'
                },
                {
                    id: 'email_002',
                    from: 'partner@lawfirm.de',
                    subject: 'Mandantenvertretung',
                    date: '2024-01-30T11:45:00Z',
                    preview: 'Bezüglich des Mandats von Herrn Schmidt...',
                    has_attachment: false,
                    status: 'read'
                }
            ],
            dashboardStats: {
                documents_created: 247,
                emails_processed: 89,
                templates_saved: 34,
                recent_activity: [
                    {
                        id: 'act_001',
                        type: 'document_created',
                        title: 'Vertrag erstellt: Kaufvertrag Immobilie',
                        timestamp: '2024-01-30T16:00:00Z',
                        icon: 'file-plus'
                    },
                    {
                        id: 'act_002',
                        type: 'email_processed',
                        title: 'E-Mail-Antwort generiert',
                        timestamp: '2024-01-30T14:30:00Z',
                        icon: 'mail'
                    }
                ]
            }
        };
    }
    
    async login(email, password) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
        
        return {
            success: true,
            token: 'mock_jwt_token_' + Date.now(),
            user: {
                id: 1,
                email: email,
                name: 'Dr. Anna Vogel',
                role: 'Administrator',
                initials: 'AV'
            }
        };
    }
    
    async getTemplates() {
        await new Promise(resolve => setTimeout(resolve, 500));
        return {
            success: true,
            templates: this.mockData.templates
        };
    }
    
    async getEmails() {
        await new Promise(resolve => setTimeout(resolve, 500));
        return {
            success: true,
            emails: this.mockData.emails
        };
    }
    
    async getDashboardStats() {
        await new Promise(resolve => setTimeout(resolve, 300));
        return this.mockData.dashboardStats;
    }
    
    async generateDocument(prompt, templateId, file) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate AI processing
        
        return {
            success: true,
            document: {
                id: 'doc_' + Date.now(),
                content: `Generiertes Dokument basierend auf: "${prompt}"\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`,
                confidence: 0.92,
                processing_time: 1.8,
                model_used: 'deepseek-ai/DeepSeek-V3',
                tokens_used: 1250
            }
        };
    }
    
    async healthCheck() {
        return true;
    }
}

// Export for use in application
window.AnwaltsAIApiClient = AnwaltsAIApiClient;
window.MockApiClient = MockApiClient;