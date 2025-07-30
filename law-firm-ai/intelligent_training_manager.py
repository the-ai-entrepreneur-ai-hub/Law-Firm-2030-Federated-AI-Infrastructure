#!/usr/bin/env python3
"""
Intelligent Training Manager for Anwalts AI
Automatically improves model performance using user feedback and RLHF
"""

import json
import time
import logging
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
import threading
import os
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float
    acceptance_rate: float
    avg_confidence: float
    response_time: float
    user_satisfaction: float
    improvement_rate: float

@dataclass
class TrainingBatch:
    """Training batch configuration"""
    examples: List[Dict]
    batch_size: int
    document_types: List[str]
    priority_score: float
    created_at: datetime

class IntelligentTrainingManager:
    """Manages intelligent model training with adaptive learning"""
    
    def __init__(self, db_path: str = "training_data.db"):
        self.db_path = db_path
        self.training_config = self._load_training_config()
        self.performance_tracker = ModelPerformanceTracker(db_path)
        self.adaptive_scheduler = AdaptiveTrainingScheduler()
        self.quality_analyzer = TrainingDataQualityAnalyzer()
        
        # Training thresholds
        self.min_examples_per_type = 20
        self.quality_threshold = 0.7
        self.performance_degradation_threshold = 0.05
        
        # Initialize performance tracking
        self._initialize_performance_tracking()
    
    def _load_training_config(self) -> Dict:
        """Load training configuration"""
        config_path = Path("law-firm-ai/local-training/training_config.json")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "learning_rate": 0.0001,
            "batch_size": 8,
            "max_epochs": 3,
            "warmup_steps": 100,
            "weight_decay": 0.01,
            "gradient_accumulation_steps": 4,
            "evaluation_steps": 100,
            "save_steps": 500,
            "model_selection_criteria": "user_preference",
            "adaptive_learning": True,
            "quality_filtering": True
        }
        
        # Save default config
        os.makedirs(config_path.parent, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_name TEXT UNIQUE,
                created_at TEXT,
                training_examples_count INTEGER,
                performance_metrics TEXT,
                model_path TEXT,
                is_active BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT,
                metric_name TEXT,
                metric_value REAL,
                document_type TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_training_need(self) -> Tuple[bool, str, float]:
        """Analyze if training is needed and determine priority"""
        
        # Get recent performance metrics
        recent_metrics = self.performance_tracker.get_recent_metrics(days=7)
        
        # Check for performance degradation
        if self._check_performance_degradation(recent_metrics):
            return True, "performance_degradation", 1.0
        
        # Check for new document types or patterns
        new_patterns = self._analyze_new_patterns()
        if new_patterns['priority'] > 0.8:
            return True, "new_patterns", new_patterns['priority']
        
        # Check for sufficient training data
        data_readiness = self._check_data_readiness()
        if data_readiness['ready'] and data_readiness['quality'] > self.quality_threshold:
            return True, "data_ready", data_readiness['quality']
        
        # Scheduled training check
        if self.adaptive_scheduler.should_train():
            return True, "scheduled", 0.6
        
        return False, "no_need", 0.0
    
    def _check_performance_degradation(self, metrics: Dict) -> bool:
        """Check if model performance has degraded"""
        if not metrics:
            return False
        
        current_acceptance = metrics.get('acceptance_rate', 0)
        historical_acceptance = self.performance_tracker.get_baseline_acceptance_rate()
        
        if historical_acceptance and current_acceptance < (historical_acceptance - self.performance_degradation_threshold):
            logger.warning(f"Performance degradation detected: {current_acceptance:.2f} vs {historical_acceptance:.2f}")
            return True
        
        return False
    
    def _analyze_new_patterns(self) -> Dict:
        """Analyze for new document patterns requiring training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent examples with low confidence or rejection
        cursor.execute('''
            SELECT document_type, feedback_type, confidence_score, prompt
            FROM training_examples
            WHERE timestamp > datetime('now', '-7 days')
            AND (confidence_score < 0.7 OR feedback_type = 'reject')
        ''')
        
        problematic_examples = cursor.fetchall()
        conn.close()
        
        if not problematic_examples:
            return {'priority': 0.0, 'types': []}
        
        # Analyze patterns
        type_issues = Counter([ex[0] for ex in problematic_examples])
        total_issues = len(problematic_examples)
        
        # Calculate priority based on issue frequency and severity
        priority = min(total_issues / 50.0, 1.0)  # Max priority when 50+ issues
        
        return {
            'priority': priority,
            'types': list(type_issues.keys()),
            'total_issues': total_issues,
            'type_breakdown': dict(type_issues)
        }
    
    def _check_data_readiness(self) -> Dict:
        """Check if we have sufficient quality data for training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get training data statistics
        cursor.execute('''
            SELECT 
                document_type,
                COUNT(*) as total,
                COUNT(CASE WHEN feedback_type = 'accept' THEN 1 END) as accepted,
                COUNT(CASE WHEN feedback_type = 'improve' AND user_edit IS NOT NULL THEN 1 END) as improved,
                AVG(confidence_score) as avg_confidence
            FROM training_examples
            WHERE feedback_type IN ('accept', 'improve')
            GROUP BY document_type
        ''')
        
        type_stats = cursor.fetchall()
        conn.close()
        
        if not type_stats:
            return {'ready': False, 'quality': 0.0}
        
        # Check readiness criteria
        ready_types = 0
        total_quality = 0
        
        for doc_type, total, accepted, improved, avg_conf in type_stats:
            usable_examples = accepted + improved
            if usable_examples >= self.min_examples_per_type:
                ready_types += 1
            total_quality += avg_conf or 0
        
        overall_quality = total_quality / len(type_stats) if type_stats else 0
        
        return {
            'ready': ready_types > 0,
            'quality': overall_quality,
            'ready_types': ready_types,
            'total_types': len(type_stats)
        }
    
    def prepare_intelligent_training_batch(self) -> Optional[TrainingBatch]:
        """Prepare intelligent training batch with quality filtering"""
        
        # Get all training data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prompt, response, feedback_type, user_edit, confidence_score, 
                   document_type, timestamp
            FROM training_examples
            WHERE feedback_type IN ('accept', 'improve', 'reject')
            ORDER BY timestamp DESC
        ''')
        
        all_examples = cursor.fetchall()
        conn.close()
        
        if not all_examples:
            return None
        
        # Process examples intelligently
        processed_examples = []
        
        for example in all_examples:
            prompt, response, feedback_type, user_edit, confidence, doc_type, timestamp = example
            
            # Quality filtering
            if not self.quality_analyzer.is_high_quality(prompt, response, confidence):
                continue
            
            # Create training pair based on feedback
            if feedback_type == 'accept':
                processed_examples.append({
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": response}
                    ],
                    "document_type": doc_type,
                    "quality_score": confidence,
                    "source": "accepted"
                })
            
            elif feedback_type == 'improve' and user_edit:
                # Use user-improved version with higher weight
                processed_examples.append({
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": user_edit}
                    ],
                    "document_type": doc_type,
                    "quality_score": min(confidence + 0.2, 1.0),  # Boost quality for improved examples
                    "source": "improved"
                })
                
                # Also add negative example (what not to do)
                processed_examples.append({
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": f"[NEGATIVE_EXAMPLE] {response}"}
                    ],
                    "document_type": doc_type,
                    "quality_score": 0.3,  # Low quality for negative examples
                    "source": "negative"
                })
        
        if not processed_examples:
            return None
        
        # Sort by quality and diversity
        processed_examples.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Balance dataset by document type
        balanced_examples = self._balance_training_data(processed_examples)
        
        # Calculate priority score
        priority_score = self._calculate_batch_priority(balanced_examples)
        
        return TrainingBatch(
            examples=balanced_examples,
            batch_size=self.training_config['batch_size'],
            document_types=list(set(ex['document_type'] for ex in balanced_examples)),
            priority_score=priority_score,
            created_at=datetime.now()
        )
    
    def _balance_training_data(self, examples: List[Dict]) -> List[Dict]:
        """Balance training data across document types"""
        type_groups = defaultdict(list)
        
        for example in examples:
            type_groups[example['document_type']].append(example)
        
        # Determine samples per type
        max_samples_per_type = 100
        min_samples_per_type = 10
        
        balanced_examples = []
        
        for doc_type, type_examples in type_groups.items():
            # Sort by quality within type
            type_examples.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # Take top examples for this type
            samples_to_take = min(max_samples_per_type, len(type_examples))
            samples_to_take = max(samples_to_take, min_samples_per_type)
            
            balanced_examples.extend(type_examples[:samples_to_take])
        
        return balanced_examples
    
    def _calculate_batch_priority(self, examples: List[Dict]) -> float:
        """Calculate priority score for training batch"""
        if not examples:
            return 0.0
        
        # Factors: data quality, diversity, recency, user demand
        quality_score = np.mean([ex['quality_score'] for ex in examples])
        diversity_score = len(set(ex['document_type'] for ex in examples)) / 10.0  # Max 10 types
        
        # Improvement potential (more improved examples = higher priority)
        improvement_count = sum(1 for ex in examples if ex['source'] == 'improved')
        improvement_score = min(improvement_count / len(examples), 1.0)
        
        # Combined priority
        priority = (quality_score * 0.4 + diversity_score * 0.3 + improvement_score * 0.3)
        
        return min(priority, 1.0)
    
    def execute_training(self, batch: TrainingBatch) -> bool:
        """Execute training with the prepared batch"""
        try:
            logger.info(f"Starting intelligent training with {len(batch.examples)} examples")
            
            # Save training data to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            training_file = Path(f"law-firm-ai/local-training/data/intelligent_training_{timestamp}.jsonl")
            
            with open(training_file, 'w', encoding='utf-8') as f:
                for example in batch.examples:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
            
            # Update training configuration based on batch characteristics
            self._adapt_training_config(batch)
            
            # Execute training
            success = self._run_training_process(training_file)
            
            if success:
                # Save model version
                self._save_model_version(batch, timestamp)
                
                # Update performance tracking
                self.performance_tracker.record_training_event(
                    version_name=f"intelligent_v{timestamp}",
                    examples_count=len(batch.examples),
                    document_types=batch.document_types
                )
                
                logger.info("Intelligent training completed successfully")
                return True
            else:
                logger.error("Training process failed")
                return False
                
        except Exception as e:
            logger.error(f"Training execution failed: {e}")
            return False
    
    def _adapt_training_config(self, batch: TrainingBatch):
        """Adapt training configuration based on batch characteristics"""
        
        # Adjust learning rate based on data complexity
        base_lr = 0.0001
        if batch.priority_score > 0.8:
            # High priority = more aggressive learning
            self.training_config['learning_rate'] = base_lr * 1.5
        elif batch.priority_score < 0.4:
            # Low priority = conservative learning
            self.training_config['learning_rate'] = base_lr * 0.7
        
        # Adjust epochs based on data size
        if len(batch.examples) > 200:
            self.training_config['max_epochs'] = 2  # More data = fewer epochs
        elif len(batch.examples) < 50:
            self.training_config['max_epochs'] = 4  # Less data = more epochs
        
        # Save updated config
        config_path = Path("law-firm-ai/local-training/training_config.json")
        with open(config_path, 'w') as f:
            json.dump(self.training_config, f, indent=2)
    
    def _run_training_process(self, training_file: Path) -> bool:
        """Run the actual training process"""
        try:
            # Change to training directory
            original_cwd = os.getcwd()
            os.chdir("law-firm-ai/local-training")
            
            # Run training script
            cmd = [
                "python", "simple_local_train.py",
                "--data_file", str(training_file),
                "--config_file", "training_config.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                logger.info("Training subprocess completed successfully")
                return True
            else:
                logger.error(f"Training subprocess failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Training process timed out")
            return False
        except Exception as e:
            logger.error(f"Training subprocess error: {e}")
            return False
    
    def _save_model_version(self, batch: TrainingBatch, timestamp: str):
        """Save model version information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metrics = {
            'examples_count': len(batch.examples),
            'document_types': batch.document_types,
            'priority_score': batch.priority_score,
            'training_config': self.training_config
        }
        
        cursor.execute('''
            INSERT INTO model_versions 
            (version_name, created_at, training_examples_count, performance_metrics, model_path, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            f"intelligent_v{timestamp}",
            datetime.now().isoformat(),
            len(batch.examples),
            json.dumps(metrics),
            f"law-firm-ai/local-training/trained_model/intelligent_v{timestamp}",
            True
        ))
        
        # Deactivate previous versions
        cursor.execute('UPDATE model_versions SET is_active = 0 WHERE version_name != ?', 
                      (f"intelligent_v{timestamp}",))
        
        conn.commit()
        conn.close()

class ModelPerformanceTracker:
    """Tracks model performance over time"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_recent_metrics(self, days: int = 7) -> Dict:
        """Get performance metrics from recent period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN feedback_type = 'accept' THEN 1 END) * 100.0 / COUNT(*) as acceptance_rate,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) as total_interactions
            FROM training_examples
            WHERE timestamp > ?
        ''', (since_date,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'acceptance_rate': result[0] or 0,
            'avg_confidence': result[1] or 0,
            'total_interactions': result[2] or 0
        }
    
    def get_baseline_acceptance_rate(self) -> Optional[float]:
        """Get baseline acceptance rate for comparison"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(metric_value)
            FROM performance_history
            WHERE metric_name = 'acceptance_rate'
            AND timestamp > datetime('now', '-30 days')
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] else None
    
    def record_training_event(self, version_name: str, examples_count: int, document_types: List[str]):
        """Record a training event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        # Record training metrics
        metrics = [
            ('examples_used', examples_count, 'training'),
            ('document_types_count', len(document_types), 'training'),
        ]
        
        for metric_name, value, doc_type in metrics:
            cursor.execute('''
                INSERT INTO performance_history (model_version, metric_name, metric_value, document_type, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (version_name, metric_name, value, doc_type, timestamp))
        
        conn.commit()
        conn.close()

class AdaptiveTrainingScheduler:
    """Manages adaptive training scheduling"""
    
    def __init__(self):
        self.last_training_time = None
        self.training_frequency = timedelta(days=1)  # Default daily
        self.performance_based_scheduling = True
    
    def should_train(self) -> bool:
        """Determine if scheduled training should occur"""
        if self.last_training_time is None:
            return True
        
        time_since_training = datetime.now() - self.last_training_time
        return time_since_training >= self.training_frequency
    
    def update_schedule_based_on_performance(self, metrics: Dict):
        """Adapt training frequency based on performance"""
        if not self.performance_based_scheduling:
            return
        
        acceptance_rate = metrics.get('acceptance_rate', 0)
        
        if acceptance_rate < 60:
            # Poor performance = train more frequently
            self.training_frequency = timedelta(hours=12)
        elif acceptance_rate > 85:
            # Good performance = train less frequently
            self.training_frequency = timedelta(days=3)
        else:
            # Average performance = default frequency
            self.training_frequency = timedelta(days=1)

class TrainingDataQualityAnalyzer:
    """Analyzes training data quality"""
    
    def is_high_quality(self, prompt: str, response: str, confidence: float) -> bool:
        """Determine if training example is high quality"""
        
        # Basic quality checks
        if len(prompt.strip()) < 10:
            return False
        
        if len(response.strip()) < 20:
            return False
        
        if confidence < 0.3:
            return False
        
        # Content quality checks
        if self._contains_inappropriate_content(prompt, response):
            return False
        
        if self._is_german_legal_content(response):
            return True
        
        return confidence > 0.5
    
    def _contains_inappropriate_content(self, prompt: str, response: str) -> bool:
        """Check for inappropriate content"""
        inappropriate_keywords = ['hate', 'violence', 'inappropriate']
        text = f"{prompt} {response}".lower()
        
        return any(keyword in text for keyword in inappropriate_keywords)
    
    def _is_german_legal_content(self, text: str) -> bool:
        """Check if content appears to be German legal content"""
        german_legal_indicators = [
            'sehr geehrte', 'mit freundlichen grüßen', 'rechtsanwalt',
            'gericht', 'klage', 'mahnung', 'vertrag', 'rechtlich'
        ]
        
        text_lower = text.lower()
        return sum(1 for indicator in german_legal_indicators if indicator in text_lower) >= 2

if __name__ == "__main__":
    # Initialize and test the intelligent training manager
    manager = IntelligentTrainingManager()
    
    # Check if training is needed
    should_train, reason, priority = manager.analyze_training_need()
    
    if should_train:
        logger.info(f"Training needed: {reason} (priority: {priority:.2f})")
        
        # Prepare training batch
        batch = manager.prepare_intelligent_training_batch()
        
        if batch:
            logger.info(f"Prepared training batch with {len(batch.examples)} examples")
            logger.info(f"Document types: {batch.document_types}")
            logger.info(f"Priority score: {batch.priority_score:.2f}")
            
            # Execute training
            success = manager.execute_training(batch)
            
            if success:
                logger.info("Intelligent training completed successfully!")
            else:
                logger.error("Training failed!")
        else:
            logger.warning("Could not prepare training batch")
    else:
        logger.info("No training needed at this time")