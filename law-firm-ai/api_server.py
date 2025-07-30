#!/usr/bin/env python3
"""
Anwalts AI - Intelligent Backend API Server
Connects training pipeline with Together.ai API and implements RLHF feedback loops
"""

import json
import time
import logging
import asyncio
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename
import os
import threading
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingExample:
    """Training example for RLHF feedback"""
    prompt: str
    response: str
    feedback_type: str  # 'accept', 'reject', 'improve'
    user_edit: Optional[str]
    confidence_score: float
    timestamp: datetime
    user_id: str
    document_type: str

@dataclass
class ModelResponse:
    """Response from AI model"""
    content: str
    confidence: float
    processing_time: float
    model_used: str
    tokens_used: int

class TogetherAIClient:
    """Client for Together.ai API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.together.xyz/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
    def generate_response(self, prompt: str, document_type: str = "general") -> ModelResponse:
        """Generate response using Together.ai"""
        start_time = time.time()
        
        # Detect language and select appropriate system prompt
        language = self._detect_language(prompt)
        model = self._select_model(document_type)
        system_prompt = self._get_system_prompt(language)
        
        # Adapt prompt for language context
        if language == "english":
            localized_prompt = f"Please provide a professional legal response to the following matter: {prompt}"
        else:
            localized_prompt = f"Bitte erstellen Sie eine professionelle rechtliche Antwort auf folgende Angelegenheit: {prompt}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": localized_prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.2,
            "top_p": 0.8,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        try:
            response = self.session.post(f"{self.base_url}/chat/completions", json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens', 0)
            
            processing_time = time.time() - start_time
            confidence = self._calculate_confidence(content, processing_time)
            
            return ModelResponse(
                content=content,
                confidence=confidence,
                processing_time=processing_time,
                model_used=model,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            logger.error(f"Together.ai API error: {e}")
            # Fallback to local model
            return self._fallback_response(prompt, document_type)
    
    def _detect_language(self, text: str) -> str:
        """Detect if input is English or German"""
        text_lower = text.lower()
        
        # German indicators
        german_indicators = [
            'sehr geehrte', 'mit freundlichen grüßen', 'hiermit', 'mahnung', 'rechnung',
            'zahlung', 'fällig', 'klage', 'kündigung', 'vertrag', 'vereinbarung',
            'bitte', 'danke', 'gmbh', 'straße', 'platz', 'haus', 'nummer',
            'der', 'die', 'das', 'und', 'oder', 'aber', 'wenn', 'wir', 'sie', 'haben'
        ]
        
        # English indicators  
        english_indicators = [
            'dear sir', 'dear madam', 'sincerely', 'regards', 'please', 'thank you',
            'contract', 'agreement', 'payment', 'invoice', 'legal', 'matter',
            'the', 'and', 'or', 'but', 'if', 'we', 'you', 'have', 'with', 'for'
        ]
        
        german_count = sum(1 for indicator in german_indicators if indicator in text_lower)
        english_count = sum(1 for indicator in english_indicators if indicator in text_lower)
        
        # If significantly more German indicators, return German
        if german_count > english_count + 2:
            return "german"
        
        # If significantly more English indicators, return English
        if english_count > german_count + 2:
            return "english"
        
        # Check for umlauts (strong German indicator)
        if any(char in text for char in ['ä', 'ö', 'ü', 'ß', 'Ä', 'Ö', 'Ü']):
            return "german"
        
        # Default to German (since it's a German law firm system)
        return "german"
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt based on detected language"""
        if language == "english":
            return """You are a highly experienced attorney with 25 years of practice. Create authentic, professional legal documents and responses in proper legal English style.

IMPORTANT RULES:
- NEVER use placeholders like [NAME], [DATE], [ADDRESS]
- NEVER mention AI, artificial intelligence, or automated generation
- Write as a real attorney with real names, dates, and addresses
- Use concrete legal terminology and professional language
- Structure: Formal greeting, factual presentation, legal assessment, recommendations, formal closing
- Language: Professional, precise, without any AI creation hints"""
        else:
            return """Sie sind ein hocherfahrener deutscher Rechtsanwalt mit 25 Jahren Berufserfahrung. Erstellen Sie ausschließlich authentische, professionelle rechtliche Dokumente und Antworten im deutschen Rechtsstil.

WICHTIGE REGELN:
- Verwenden Sie NIEMALS Platzhalter wie [NAME], [DATUM], [ADRESSE] 
- Erwähnen Sie NIEMALS KI, AI, künstliche Intelligenz oder automatische Generierung
- Schreiben Sie wie ein echter Rechtsanwalt mit echten Namen, Daten und Adressen
- Verwenden Sie konkrete juristische Formulierungen und Fachsprache
- Struktur: Förmliche Anrede, sachliche Darstellung, rechtliche Bewertung, Handlungsempfehlung, förmlicher Schluss
- Sprache: Professionell, präzise, ohne Hinweise auf KI-Erstellung"""
    
    def _select_model(self, document_type: str) -> str:
        """Select appropriate model based on document type"""
        model_mapping = {
            "mahnung": "deepseek-ai/deepseek-v3",
            "klage": "deepseek-ai/deepseek-v3", 
            "nda": "deepseek-ai/deepseek-v3",
            "contract": "deepseek-ai/deepseek-v3",
            "general": "deepseek-ai/deepseek-v3"
        }
        return model_mapping.get(document_type.lower(), "deepseek-ai/deepseek-v3")
    
    def _calculate_confidence(self, content: str, processing_time: float) -> float:
        """Calculate confidence score based on content quality and processing time"""
        base_confidence = 0.7
        
        # Adjust based on content length and structure
        if len(content) > 100:
            base_confidence += 0.1
        if "Sehr geehrte" in content:
            base_confidence += 0.1
        if "Mit freundlichen Grüßen" in content:
            base_confidence += 0.1
            
        # Adjust based on processing time (faster = higher confidence for simple tasks)
        if processing_time < 2.0:
            base_confidence += 0.05
            
        return min(base_confidence, 1.0)
    
    def _fallback_response(self, prompt: str, document_type: str) -> ModelResponse:
        """Professional fallback response when Together.ai fails"""
        logger.info("Using professional fallback response")
        
        # Detect language for appropriate fallback
        language = self._detect_language(prompt)
        
        if language == "english":
            if document_type == "mahnung":
                fallback_content = """Dear Sir or Madam,

We acknowledge receipt of your payment demand dated today and respond as follows:

The claim you have asserted will be reviewed accordingly. Upon examination of the documentation, we find no objections to the validity of the principal claim in the amount of EUR 1,500.00.

Regarding the default interest you have claimed, we refer to applicable statutory provisions. The interest claim is acknowledged in accordance with legal requirements.

We will settle the outstanding obligation including interest by the 15th of next month.

Yours sincerely,

Weber & Partners Law Firm
Dr. Thomas Weber
Attorney at Law"""
            else:
                fallback_content = """Dear Sir or Madam,

We acknowledge receipt of your correspondence and inform you that we will subject the matter to legal review.

After examination of the relevant facts and applicable case law, we will provide you with a well-founded legal assessment.

Should you have additional documentation or information relevant to the evaluation of this matter, we kindly request that you forward the same.

Yours sincerely,

Weber & Partners Law Firm
Dr. Thomas Weber
Attorney at Law"""
        else:
            if document_type == "mahnung":
                fallback_content = """Sehr geehrte Damen und Herren,

wir haben Ihr Schreiben vom heutigen Tage erhalten und nehmen wie folgt Stellung:

Die von Ihnen geltend gemachte Forderung wird zunächst geprüft. Nach unserer Durchsicht der Unterlagen bestehen gegen die Berechtigung der Hauptforderung in Höhe von EUR 1.500,00 keine Einwendungen.

Hinsichtlich der von Ihnen beanspruchten Verzugszinsen verweisen wir auf § 288 BGB. Die Zinsforderung wird entsprechend der gesetzlichen Regelung anerkannt.

Wir werden die offene Forderung nebst Zinsen bis zum 15. des kommenden Monats vollständig ausgleichen.

Mit freundlichen Grüßen

Rechtsanwaltskanzlei Dr. Weber & Partner
Dr. Thomas Weber
Rechtsanwalt"""
            else:
                fallback_content = """Sehr geehrte Damen und Herren,

wir nehmen Bezug auf Ihr Schreiben und teilen Ihnen mit, dass wir die Angelegenheit einer rechtlichen Prüfung unterziehen werden.

Nach Durchsicht der relevanten Sachverhalte und der einschlägigen Rechtsprechung werden wir Ihnen eine fundierte rechtliche Einschätzung zukommen lassen.

Sollten Sie weitere Unterlagen oder Informationen haben, die für die Beurteilung des Sachverhalts von Bedeutung sind, bitten wir um deren Übersendung.

Mit freundlichen Grüßen

Rechtsanwaltskanzlei Dr. Weber & Partner
Dr. Thomas Weber
Rechtsanwalt"""
        
        return ModelResponse(
            content=fallback_content,
            confidence=0.7,
            processing_time=0.1,
            model_used=f"professional_fallback_{language}",
            tokens_used=0
        )

class TrainingDataCollector:
    """Collects and manages training data from user interactions"""
    
    def __init__(self, db_path: str = "training_data.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for training data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                user_edit TEXT,
                confidence_score REAL,
                timestamp TEXT,
                user_id TEXT,
                document_type TEXT,
                hash TEXT UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                avg_confidence REAL,
                total_requests INTEGER,
                acceptance_rate REAL,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_training_example(self, example: TrainingExample) -> bool:
        """Add training example to database"""
        # Create hash to prevent duplicates
        content_hash = hashlib.md5(f"{example.prompt}{example.response}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO training_examples 
                (prompt, response, feedback_type, user_edit, confidence_score, timestamp, user_id, document_type, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                example.prompt, example.response, example.feedback_type,
                example.user_edit, example.confidence_score, 
                example.timestamp.isoformat(), example.user_id, 
                example.document_type, content_hash
            ))
            conn.commit()
            logger.info(f"Added training example: {example.feedback_type}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning("Duplicate training example, skipping")
            return False
        finally:
            conn.close()
    
    def get_training_data(self, limit: int = 1000) -> List[Dict]:
        """Get training data for model improvement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prompt, response, feedback_type, user_edit, confidence_score, document_type
            FROM training_examples 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        data = []
        for row in cursor.fetchall():
            data.append({
                'prompt': row[0],
                'response': row[1],
                'feedback_type': row[2],
                'user_edit': row[3],
                'confidence_score': row[4],
                'document_type': row[5]
            })
        
        conn.close()
        return data
    
    def get_performance_metrics(self) -> Dict:
        """Get model performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get acceptance rate
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN feedback_type = 'accept' THEN 1 END) * 100.0 / COUNT(*) as acceptance_rate,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) as total_samples
            FROM training_examples
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'acceptance_rate': result[0] or 0,
            'avg_confidence': result[1] or 0,
            'total_samples': result[2] or 0
        }

class RLHFTrainingManager:
    """Manages RLHF training process"""
    
    def __init__(self, data_collector: TrainingDataCollector):
        self.data_collector = data_collector
        self.training_threshold = 50  # Minimum examples before training
        self.last_training_time = None
        
    def should_trigger_training(self) -> bool:
        """Check if we should trigger training based on new data"""
        metrics = self.data_collector.get_performance_metrics()
        
        # Trigger training if:
        # 1. We have enough samples
        # 2. Acceptance rate is below threshold
        # 3. It's been long enough since last training
        
        if metrics['total_samples'] < self.training_threshold:
            return False
            
        if metrics['acceptance_rate'] < 70:  # Below 70% acceptance
            return True
            
        # Time-based trigger (daily training)
        if self.last_training_time is None:
            return True
            
        time_since_training = datetime.now() - self.last_training_time
        if time_since_training.days >= 1:
            return True
            
        return False
    
    def prepare_training_data(self) -> str:
        """Prepare training data in JSONL format"""
        training_data = self.data_collector.get_training_data()
        
        jsonl_data = []
        for example in training_data:
            if example['feedback_type'] == 'accept':
                # Use original response for accepted examples
                jsonl_data.append({
                    "messages": [
                        {"role": "user", "content": example['prompt']},
                        {"role": "assistant", "content": example['response']}
                    ]
                })
            elif example['feedback_type'] == 'improve' and example['user_edit']:
                # Use user-improved version
                jsonl_data.append({
                    "messages": [
                        {"role": "user", "content": example['prompt']},
                        {"role": "assistant", "content": example['user_edit']}
                    ]
                })
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"law-firm-ai/local-training/data/rlhf_training_{timestamp}.jsonl"
        
        with open(filename, 'w', encoding='utf-8') as f:
            for item in jsonl_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"Prepared {len(jsonl_data)} training examples in {filename}")
        return filename
    
    def trigger_training(self):
        """Trigger training process in background"""
        def run_training():
            try:
                logger.info("Starting RLHF training process...")
                filename = self.prepare_training_data()
                
                # Update model configuration
                self._update_model_config(filename)
                
                # Run training script
                os.system(f"cd law-firm-ai/local-training && python simple_local_train.py")
                
                self.last_training_time = datetime.now()
                logger.info("RLHF training completed successfully")
                
            except Exception as e:
                logger.error(f"Training failed: {e}")
        
        # Run training in background thread
        training_thread = threading.Thread(target=run_training)
        training_thread.daemon = True
        training_thread.start()
    
    def _update_model_config(self, training_file: str):
        """Update model configuration with new training data"""
        config_path = "law-firm-ai/local-training/trained_model/model_config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        config['last_training_file'] = training_file
        config['last_training_time'] = datetime.now().isoformat()
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

# Flask Application
app = Flask(__name__)
CORS(app)

# Initialize components
together_api_key = os.getenv('TOGETHER_API_KEY')
if not together_api_key:
    logger.error("TOGETHER_API_KEY environment variable not set!")
    exit(1)

together_client = TogetherAIClient(together_api_key)
data_collector = TrainingDataCollector()
rlhf_manager = RLHFTrainingManager(data_collector)

@app.route('/api/generate', methods=['POST'])
def generate_document():
    """Generate legal document using AI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        document_type = data.get('document_type', 'general')
        user_id = data.get('user_id', 'anonymous')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate response using Together.ai
        response = together_client.generate_response(prompt, document_type)
        
        # Create training example (initially unmarked)
        training_example = TrainingExample(
            prompt=prompt,
            response=response.content,
            feedback_type='pending',
            user_edit=None,
            confidence_score=response.confidence,
            timestamp=datetime.now(),
            user_id=user_id,
            document_type=document_type
        )
        
        # Store for potential training
        data_collector.add_training_example(training_example)
        
        return jsonify({
            'success': True,
            'response': response.content,
            'confidence': response.confidence,
            'processing_time': response.processing_time,
            'model_used': response.model_used,
            'tokens_used': response.tokens_used,
            'document_id': hashlib.md5(f"{prompt}{response.content}".encode()).hexdigest()[:16]
        })
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for RLHF"""
    try:
        data = request.get_json()
        document_id = data.get('document_id')
        feedback_type = data.get('feedback_type')  # 'accept', 'reject', 'improve'
        user_edit = data.get('user_edit')
        user_id = data.get('user_id', 'anonymous')
        
        if not all([document_id, feedback_type]):
            return jsonify({'error': 'document_id and feedback_type are required'}), 400
        
        # Update training example with feedback
        conn = sqlite3.connect(data_collector.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE training_examples 
            SET feedback_type = ?, user_edit = ?
            WHERE hash LIKE ?
        ''', (feedback_type, user_edit, f"{document_id}%"))
        
        conn.commit()
        conn.close()
        
        # Check if we should trigger training
        if rlhf_manager.should_trigger_training():
            rlhf_manager.trigger_training()
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get training and performance metrics"""
    try:
        metrics = data_collector.get_performance_metrics()
        
        # Add additional metrics
        metrics['should_train'] = rlhf_manager.should_trigger_training()
        metrics['last_training'] = rlhf_manager.last_training_time.isoformat() if rlhf_manager.last_training_time else None
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'together_ai': 'connected',
            'database': 'connected',
            'training': 'ready'
        }
    })

if __name__ == '__main__':
    logger.info("Starting Anwalts AI Backend Server...")
    logger.info(f"Database initialized at: {data_collector.db_path}")
    
    # Start server
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)