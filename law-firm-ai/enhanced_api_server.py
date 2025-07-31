#!/usr/bin/env python3
"""
Enhanced AnwaltsAI API Server
Complete backend for the AnwaltsAI application with authentication, document generation, and RLHF
"""

import json
import time
import logging
import sqlite3
import hashlib
import jwt
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'anwalts-ai-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Enable CORS
CORS(app, origins=["http://localhost:8080", "http://127.0.0.1:8080", "*"])

# =========================
# DATA MODELS
# =========================

@dataclass
class User:
    id: str
    email: str
    name: str
    role: str  # 'admin' or 'assistant'
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None

@dataclass
class Document:
    id: str
    user_id: str
    prompt: str
    content: str
    template_id: Optional[str]
    feedback_type: Optional[str]  # 'accept', 'reject', 'improve'
    confidence: float
    processing_time: float
    model_used: str
    tokens_used: int
    created_at: datetime

@dataclass
class Template:
    id: str
    name: str
    content: str
    category: str
    type: str  # 'system', 'personal', 'firm'
    user_id: Optional[str]
    usage_count: int
    created_at: datetime

@dataclass
class Email:
    id: str
    from_address: str
    subject: str
    content: str
    date: datetime
    has_attachment: bool
    status: str  # 'read', 'unread'
    ai_response: Optional[str] = None

# =========================
# DATABASE SETUP
# =========================

class DatabaseManager:
    def __init__(self, db_path="anwalts_ai.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    prompt TEXT,
                    content TEXT,
                    template_id TEXT,
                    feedback_type TEXT,
                    confidence REAL,
                    processing_time REAL,
                    model_used TEXT,
                    tokens_used INTEGER,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Templates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL,
                    user_id TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Emails table (for mock data)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    from_address TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    content TEXT NOT NULL,
                    date TIMESTAMP,
                    has_attachment BOOLEAN,
                    status TEXT DEFAULT 'unread',
                    ai_response TEXT
                )
            ''')
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    document_id TEXT,
                    user_id TEXT,
                    feedback_type TEXT,
                    user_edit TEXT,
                    comment TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
            # Insert default data
            self.insert_default_data()
    
    def insert_default_data(self):
        """Insert default users, templates, and mock emails"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Default admin user
            cursor.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                default_user = User(
                    id=str(uuid.uuid4()),
                    email='admin@anwalts-ai.de',
                    name='Dr. Anna Vogel',
                    role='admin',
                    password_hash=hashlib.sha256('admin123'.encode()).hexdigest(),
                    created_at=datetime.now()
                )
                
                cursor.execute('''
                    INSERT INTO users (id, email, name, role, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (default_user.id, default_user.email, default_user.name, 
                     default_user.role, default_user.password_hash, default_user.created_at))
                
                logger.info("Default admin user created: admin@anwalts-ai.de / admin123")
            
            # Default templates
            cursor.execute('SELECT COUNT(*) FROM templates')
            if cursor.fetchone()[0] == 0:
                default_templates = [
                    Template(
                        id=str(uuid.uuid4()),
                        name='Mahnung (1. Stufe)',
                        content='Sehr geehrte Damen und Herren,\n\nhiermit mahnen wir Sie zur Zahlung der offenen Rechnung Nr. [RECHNUNGSNUMMER] vom [DATUM] über [BETRAG] €.\n\nWir bitten Sie, den Betrag innerhalb von 14 Tagen zu begleichen.\n\nMit freundlichen Grüßen',
                        category='payment',
                        type='system',
                        user_id=None,
                        usage_count=0,
                        created_at=datetime.now()
                    ),
                    Template(
                        id=str(uuid.uuid4()),
                        name='Geheimhaltungsvereinbarung',
                        content='GEHEIMHALTUNGSVEREINBARUNG\n\nZwischen [PARTEI_1] und [PARTEI_2] wird folgende Geheimhaltungsvereinbarung geschlossen:\n\n1. Gegenstand\nDie Parteien beabsichtigen...',
                        category='contracts',
                        type='system',
                        user_id=None,
                        usage_count=0,
                        created_at=datetime.now()
                    ),
                    Template(
                        id=str(uuid.uuid4()),
                        name='Kündigung Arbeitsvertrag',
                        content='Sehr geehrte/r [NAME],\n\nhiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis ordentlich zum [DATUM].\n\nDie Kündigungsfrist beträgt gemäß [GRUNDLAGE] ...',
                        category='employment',
                        type='system',
                        user_id=None,
                        usage_count=0,
                        created_at=datetime.now()
                    )
                ]
                
                for template in default_templates:
                    cursor.execute('''
                        INSERT INTO templates (id, name, content, category, type, user_id, usage_count, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (template.id, template.name, template.content, template.category,
                         template.type, template.user_id, template.usage_count, template.created_at))
                
                logger.info("Default templates created")
            
            # Mock emails
            cursor.execute('SELECT COUNT(*) FROM emails')
            if cursor.fetchone()[0] == 0:
                mock_emails = [
                    Email(
                        id=str(uuid.uuid4()),
                        from_address='client@example.com',
                        subject='Anfrage Kaufvertrag Immobilie',
                        content='Sehr geehrte Damen und Herren,\n\nich benötige Unterstützung beim Kauf einer Immobilie in München. Könnten Sie mir einen Kaufvertrag erstellen?\n\nMit freundlichen Grüßen\nMax Mustermann',
                        date=datetime.now() - timedelta(hours=2),
                        has_attachment=True,
                        status='unread'
                    ),
                    Email(
                        id=str(uuid.uuid4()),
                        from_address='partner@lawfirm.de',
                        subject='Mandantenvertretung - Herr Schmidt',
                        content='Liebe Kollegin,\n\nbezüglich des Mandats von Herrn Schmidt möchte ich Sie über den aktuellen Stand informieren...',
                        date=datetime.now() - timedelta(hours=5),
                        has_attachment=False,
                        status='read'
                    ),
                    Email(
                        id=str(uuid.uuid4()),
                        from_address='opposing@counsel.de',
                        subject='Vergleichsvorschlag - Sache Weber',
                        content='Sehr geehrte Damen und Herren,\n\nin der Sache Weber ./. Mueller möchten wir Ihnen folgenden Vergleichsvorschlag unterbreiten...',
                        date=datetime.now() - timedelta(days=1),
                        has_attachment=True,
                        status='unread'
                    )
                ]
                
                for email in mock_emails:
                    cursor.execute('''
                        INSERT INTO emails (id, from_address, subject, content, date, has_attachment, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (email.id, email.from_address, email.subject, email.content,
                         email.date, email.has_attachment, email.status))
                
                logger.info("Mock emails created")
            
            conn.commit()

# =========================
# AI CLIENT
# =========================

class TogetherAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.together.xyz/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def generate_document(self, prompt: str, template_content: str = None) -> Dict:
        """Generate legal document using AI"""
        start_time = time.time()
        
        system_prompt = """Sie sind ein erfahrener deutscher Rechtsanwalt. Erstellen Sie professionelle, rechtlich korrekte Dokumente auf Deutsch. 
        Verwenden Sie formelle Sprache und beachten Sie deutsches Recht. Strukturieren Sie Dokumente klar und logisch."""
        
        if template_content:
            user_prompt = f"Basierend auf dieser Vorlage:\n\n{template_content}\n\nErstellen Sie ein Dokument für: {prompt}"
        else:
            user_prompt = f"Erstellen Sie ein professionelles Rechtsdokument für: {prompt}"
        
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.2,
            "top_p": 0.8
        }
        
        try:
            response = self.session.post(f"{self.base_url}/chat/completions", json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens', 0)
            processing_time = time.time() - start_time
            
            return {
                'content': content,
                'confidence': 0.85 + (0.1 * min(processing_time, 5) / 5),  # Mock confidence
                'processing_time': processing_time,
                'model_used': 'deepseek-ai/DeepSeek-V3',
                'tokens_used': tokens_used
            }
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            # Fallback response
            processing_time = time.time() - start_time
            return {
                'content': f"[MOCKUP] Rechtsdokument für: {prompt}\n\nSehr geehrte Damen und Herren,\n\nhiermit erstelle ich das gewünschte Dokument...\n\n[Weitere Inhalte würden hier von der KI generiert]\n\nMit freundlichen Grüßen",
                'confidence': 0.75,
                'processing_time': processing_time,
                'model_used': 'fallback-model',
                'tokens_used': 250
            }

# =========================
# AUTHENTICATION
# =========================

def generate_jwt_token(user_id: str, email: str, role: str) -> str:
    """Generate JWT token for user authentication"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[Dict]:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_jwt_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.current_user = user_data
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

# Initialize components
db = DatabaseManager()
ai_client = TogetherAIClient(os.getenv('TOGETHER_API_KEY', 'demo-key'))

# =========================
# API ENDPOINTS
# =========================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Authentication Endpoints
@app.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email und Passwort erforderlich'}), 400
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, email, name, role, password_hash FROM users WHERE email = ?', (email,))
            user_row = cursor.fetchone()
            
            if not user_row:
                return jsonify({'error': 'Ungültige Anmeldedaten'}), 401
            
            user_id, user_email, name, role, stored_hash = user_row
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash != stored_hash:
                return jsonify({'error': 'Ungültige Anmeldedaten'}), 401
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_id))
            conn.commit()
            
            # Generate JWT token
            token = generate_jwt_token(user_id, user_email, role)
            
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'email': user_email,
                    'name': name,
                    'role': role,
                    'initials': ''.join([n[0].upper() for n in name.split()[:2]])
                }
            })
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Anmeldung fehlgeschlagen'}), 500

@app.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint"""
    return jsonify({'success': True, 'message': 'Erfolgreich abgemeldet'})

@app.route('/auth/validate', methods=['GET'])
@require_auth
def validate_token():
    """Validate JWT token"""
    return jsonify({'valid': True, 'user': request.current_user})

# Dashboard Endpoints
@app.route('/dashboard/stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Documents created by user
            cursor.execute('SELECT COUNT(*) FROM documents WHERE user_id = ?', (request.current_user['user_id'],))
            documents_created = cursor.fetchone()[0]
            
            # Emails processed (mock data for now)
            cursor.execute('SELECT COUNT(*) FROM emails WHERE ai_response IS NOT NULL')
            emails_processed = cursor.fetchone()[0]
            
            # Templates saved by user
            cursor.execute('SELECT COUNT(*) FROM templates WHERE user_id = ? OR type = "system"', (request.current_user['user_id'],))
            templates_saved = cursor.fetchone()[0]
            
            # Recent activity
            cursor.execute('''
                SELECT prompt, created_at FROM documents 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 5
            ''', (request.current_user['user_id'],))
            
            recent_activity = []
            for row in cursor.fetchall():
                prompt, created_at = row
                recent_activity.append({
                    'id': str(uuid.uuid4()),
                    'type': 'document_created',
                    'title': f'Dokument erstellt: {prompt[:50]}...' if len(prompt) > 50 else f'Dokument erstellt: {prompt}',
                    'timestamp': created_at,
                    'icon': 'file-plus'
                })
            
            return jsonify({
                'documents_created': documents_created,
                'emails_processed': emails_processed,
                'templates_saved': templates_saved,
                'recent_activity': recent_activity
            })
            
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({'error': 'Statistiken konnten nicht geladen werden'}), 500

# Document Generation Endpoints
@app.route('/generate-document', methods=['POST'])
@require_auth
def generate_document():
    """Generate legal document using AI"""
    try:
        # Handle both JSON and form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            prompt = request.form.get('prompt')
            template_id = request.form.get('template_id')
            file = request.files.get('file')
        else:
            data = request.get_json()
            prompt = data.get('prompt')
            template_id = data.get('template_id')
            file = None
        
        if not prompt:
            return jsonify({'error': 'Prompt erforderlich'}), 400
        
        # Get template content if template_id provided
        template_content = None
        if template_id:
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT content FROM templates WHERE id = ?', (template_id,))
                template_row = cursor.fetchone()
                if template_row:
                    template_content = template_row[0]
        
        # Generate document using AI
        ai_response = ai_client.generate_document(prompt, template_content)
        
        # Save document to database
        document_id = str(uuid.uuid4())
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (id, user_id, prompt, content, template_id, confidence, 
                                     processing_time, model_used, tokens_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (document_id, request.current_user['user_id'], prompt, ai_response['content'],
                 template_id, ai_response['confidence'], ai_response['processing_time'],
                 ai_response['model_used'], ai_response['tokens_used'], datetime.now()))
            conn.commit()
        
        return jsonify({
            'success': True,
            'document': {
                'id': document_id,
                'content': ai_response['content'],
                'confidence': ai_response['confidence'],
                'processing_time': ai_response['processing_time'],
                'model_used': ai_response['model_used'],
                'tokens_used': ai_response['tokens_used']
            }
        })
        
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        return jsonify({'error': 'Dokumentenerstellung fehlgeschlagen'}), 500

@app.route('/feedback', methods=['POST'])
@require_auth
def submit_feedback():
    """Submit feedback for RLHF"""
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        feedback_type = data.get('feedback_type')  # 'accept', 'reject', 'improve'
        user_edit = data.get('user_edit')
        comment = data.get('comment')
        
        if not document_id or not feedback_type:
            return jsonify({'error': 'Dokument-ID und Feedback-Typ erforderlich'}), 400
        
        # Save feedback
        feedback_id = str(uuid.uuid4())
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (id, document_id, user_id, feedback_type, user_edit, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (feedback_id, document_id, request.current_user['user_id'], 
                 feedback_type, user_edit, comment, datetime.now()))
            
            # Update document with feedback
            cursor.execute('UPDATE documents SET feedback_type = ? WHERE id = ?', 
                          (feedback_type, document_id))
            conn.commit()
        
        logger.info(f"Feedback received: {feedback_type} for document {document_id}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback erfolgreich übermittelt'
        })
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'error': 'Feedback konnte nicht übermittelt werden'}), 500

# Template Endpoints
@app.route('/templates', methods=['GET'])
@require_auth
def get_templates():
    """Get all templates"""
    try:
        category = request.args.get('category', 'all')
        template_type = request.args.get('type', 'all')
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, name, content, category, type, user_id, usage_count, created_at
                FROM templates
                WHERE (type = 'system' OR user_id = ?)
            '''
            params = [request.current_user['user_id']]
            
            if category != 'all':
                query += ' AND category = ?'
                params.append(category)
            
            if template_type != 'all':
                query += ' AND type = ?'
                params.append(template_type)
            
            query += ' ORDER BY type, name'
            
            cursor.execute(query, params)
            templates = []
            
            for row in cursor.fetchall():
                templates.append({
                    'id': row[0],
                    'name': row[1],
                    'content': row[2],
                    'category': row[3],
                    'type': row[4],
                    'user_id': row[5],
                    'usage_count': row[6],
                    'created_at': row[7]
                })
            
            return jsonify({
                'success': True,
                'templates': templates
            })
            
    except Exception as e:
        logger.error(f"Templates fetch error: {e}")
        return jsonify({'error': 'Vorlagen konnten nicht geladen werden'}), 500

@app.route('/templates', methods=['POST'])
@require_auth
def create_template():
    """Create new template"""
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        category = data.get('category')
        template_type = data.get('type', 'personal')
        
        if not name or not content or not category:
            return jsonify({'error': 'Name, Inhalt und Kategorie erforderlich'}), 400
        
        template_id = str(uuid.uuid4())
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO templates (id, name, content, category, type, user_id, usage_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (template_id, name, content, category, template_type, 
                 request.current_user['user_id'], 0, datetime.now()))
            conn.commit()
        
        return jsonify({
            'success': True,
            'template': {
                'id': template_id,
                'name': name,
                'content': content,
                'category': category,
                'type': template_type
            }
        })
        
    except Exception as e:
        logger.error(f"Template creation error: {e}")
        return jsonify({'error': 'Vorlage konnte nicht erstellt werden'}), 500

# Email Endpoints
@app.route('/emails', methods=['GET'])
@require_auth
def get_emails():
    """Get emails (mock data)"""
    try:
        filter_type = request.args.get('filter', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT id, from_address, subject, content, date, has_attachment, status, ai_response FROM emails'
            params = []
            
            if filter_type == 'unread':
                query += ' WHERE status = ?'
                params.append('unread')
            elif filter_type == 'ai_responses':
                query += ' WHERE ai_response IS NOT NULL'
            
            query += ' ORDER BY date DESC LIMIT ? OFFSET ?'
            params.extend([limit, (page - 1) * limit])
            
            cursor.execute(query, params)
            emails = []
            
            for row in cursor.fetchall():
                emails.append({
                    'id': row[0],
                    'from': row[1],
                    'subject': row[2],
                    'content': row[3],
                    'date': row[4],
                    'has_attachment': bool(row[5]),
                    'status': row[6],
                    'ai_response': row[7],
                    'preview': row[3][:100] + '...' if len(row[3]) > 100 else row[3]
                })
            
            return jsonify({
                'success': True,
                'emails': emails
            })
            
    except Exception as e:
        logger.error(f"Emails fetch error: {e}")
        return jsonify({'error': 'E-Mails konnten nicht geladen werden'}), 500

if __name__ == '__main__':
    logger.info("Starting Enhanced AnwaltsAI API Server...")
    logger.info("Default login: admin@anwalts-ai.de / admin123")
    app.run(host='0.0.0.0', port=5001, debug=True)