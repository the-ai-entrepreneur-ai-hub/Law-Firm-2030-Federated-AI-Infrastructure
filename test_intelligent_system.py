#!/usr/bin/env python3
"""
Comprehensive Test Suite for Intelligent Anwalts AI System
Tests all components: API, training pipeline, frontend integration, and RLHF
"""

import json
import time
import requests
import sqlite3
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentSystemTester:
    """Comprehensive test suite for the Intelligent Anwalts AI System"""
    
    def __init__(self):
        self.api_base = "http://localhost:5001"
        self.web_base = "http://localhost:8080" 
        self.project_root = Path(__file__).parent
        self.test_results = []
        
    def print_test_banner(self):
        """Print test banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║              INTELLIGENT ANWALTS AI SYSTEM TESTS            ║
║                   Comprehensive Test Suite                  ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def test_api_health(self) -> bool:
        """Test API server health"""
        logger.info("🔍 Testing API server health...")
        
        try:
            response = requests.get(f"{self.api_base}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API Health: {data.get('status', 'unknown')}")
                return True
            else:
                logger.error(f"❌ API health check failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ API server not accessible: {e}")
            return False
    
    def test_document_generation(self) -> bool:
        """Test intelligent document generation"""
        logger.info("🤖 Testing intelligent document generation...")
        
        test_prompt = """
        Sehr geehrte Damen und Herren,
        
        hiermit mahne ich die ausstehende Zahlung für Rechnung Nr. 2024-001 
        über den Betrag von 1.500,00 EUR an. 
        
        Die Zahlung war bereits am 15.01.2024 fällig.
        
        Mit freundlichen Grüßen
        Max Mustermann
        """
        
        try:
            payload = {
                "prompt": f"Bitte erstellen Sie eine professionelle rechtliche Antwort auf folgendes Dokument:\n\n{test_prompt}",
                "document_type": "mahnung",
                "user_id": "test_user_001"
            }
            
            response = requests.post(
                f"{self.api_base}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and data.get('response'):
                    logger.info("✅ Document generation successful")
                    logger.info(f"   Model used: {data.get('model_used', 'unknown')}")
                    logger.info(f"   Confidence: {data.get('confidence', 0):.2f}")
                    logger.info(f"   Processing time: {data.get('processing_time', 0):.2f}s")
                    logger.info(f"   Document ID: {data.get('document_id', 'none')}")
                    
                    # Store document ID for feedback test
                    self.test_document_id = data.get('document_id')
                    return True
                else:
                    logger.error("❌ Document generation failed: Invalid response format")
                    return False
            else:
                logger.error(f"❌ Document generation failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Document generation request failed: {e}")
            return False
    
    def test_feedback_submission(self) -> bool:
        """Test RLHF feedback submission"""
        logger.info("💭 Testing feedback submission...")
        
        if not hasattr(self, 'test_document_id') or not self.test_document_id:
            logger.error("❌ No document ID available for feedback test")
            return False
        
        # Test acceptance feedback
        try:
            feedback_payload = {
                "document_id": self.test_document_id,
                "feedback_type": "accept",
                "user_id": "test_user_001"
            }
            
            response = requests.post(
                f"{self.api_base}/api/feedback",
                json=feedback_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info("✅ Feedback submission successful")
                    return True
                else:
                    logger.error(f"❌ Feedback submission failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error(f"❌ Feedback submission failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Feedback submission request failed: {e}")
            return False
    
    def test_improvement_feedback(self) -> bool:
        """Test improvement feedback with user edits"""
        logger.info("✏️ Testing improvement feedback...")
        
        if not hasattr(self, 'test_document_id') or not self.test_document_id:
            logger.error("❌ No document ID available for improvement test")
            return False
        
        improved_text = """
        Sehr geehrte Damen und Herren,
        
        wir haben Ihr Schreiben bezüglich der ausstehenden Zahlung erhalten 
        und werden uns umgehend um die Begleichung der Rechnung kümmern.
        
        Die Zahlung wird innerhalb der nächsten 5 Werktage erfolgen.
        
        Wir entschuldigen uns für die Verzögerung.
        
        Mit freundlichen Grüßen
        Rechtsanwaltskanzlei Muster
        """
        
        try:
            improvement_payload = {
                "document_id": self.test_document_id,
                "feedback_type": "improve",
                "user_edit": improved_text,
                "user_id": "test_user_001"
            }
            
            response = requests.post(
                f"{self.api_base}/api/feedback",
                json=improvement_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info("✅ Improvement feedback successful")
                    return True
                else:
                    logger.error(f"❌ Improvement feedback failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error(f"❌ Improvement feedback failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Improvement feedback request failed: {e}")
            return False
    
    def test_metrics_collection(self) -> bool:
        """Test metrics and performance tracking"""
        logger.info("📊 Testing metrics collection...")
        
        try:
            response = requests.get(f"{self.api_base}/api/metrics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info("✅ Metrics collection successful")
                logger.info(f"   Acceptance rate: {data.get('acceptance_rate', 0):.1f}%")
                logger.info(f"   Average confidence: {data.get('avg_confidence', 0):.2f}")
                logger.info(f"   Total samples: {data.get('total_samples', 0)}")
                logger.info(f"   Should train: {data.get('should_train', False)}")
                
                return True
            else:
                logger.error(f"❌ Metrics collection failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Metrics request failed: {e}")
            return False
    
    def test_database_operations(self) -> bool:
        """Test database operations and storage"""
        logger.info("💾 Testing database operations...")
        
        db_path = self.project_root / "law-firm-ai" / "training_data.db"
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Test training examples table
            cursor.execute("SELECT COUNT(*) FROM training_examples")
            example_count = cursor.fetchone()[0]
            logger.info(f"   Training examples in DB: {example_count}")
            
            # Test model versions table (if exists)
            try:
                cursor.execute("SELECT COUNT(*) FROM model_versions")
                version_count = cursor.fetchone()[0]
                logger.info(f"   Model versions in DB: {version_count}")
            except sqlite3.OperationalError:
                logger.info("   Model versions table not yet created")
            
            conn.close()
            logger.info("✅ Database operations successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database operations failed: {e}")
            return False
    
    def test_training_readiness(self) -> bool:
        """Test training system readiness"""
        logger.info("🎯 Testing training system readiness...")
        
        try:
            # Import training manager
            import sys
            sys.path.append(str(self.project_root / "law-firm-ai"))
            
            from intelligent_training_manager import IntelligentTrainingManager
            
            manager = IntelligentTrainingManager()
            
            # Check training readiness
            should_train, reason, priority = manager.analyze_training_need()
            
            logger.info(f"   Should train: {should_train}")
            logger.info(f"   Reason: {reason}")
            logger.info(f"   Priority: {priority:.2f}")
            
            # Test batch preparation
            batch = manager.prepare_intelligent_training_batch()
            
            if batch:
                logger.info(f"   Training batch ready: {len(batch.examples)} examples")
                logger.info(f"   Document types: {batch.document_types}")
                logger.info(f"   Batch priority: {batch.priority_score:.2f}")
            else:
                logger.info("   No training batch available (normal for fresh installation)")
            
            logger.info("✅ Training system readiness check successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Training system test failed: {e}")
            return False
    
    def test_web_interface_accessibility(self) -> bool:
        """Test web interface accessibility"""
        logger.info("🌐 Testing web interface...")
        
        try:
            response = requests.get(self.web_base, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for key elements
                checks = [
                    ("Upload form", "upload-form" in content),
                    ("File input", "file-input" in content),
                    ("Submit button", "submit-button" in content),
                    ("Results container", "results-container" in content),
                    ("JavaScript", "script.js" in content),
                    ("CSS", "style.css" in content)
                ]
                
                all_passed = True
                for check_name, passed in checks:
                    if passed:
                        logger.info(f"   ✅ {check_name}")
                    else:
                        logger.error(f"   ❌ {check_name}")
                        all_passed = False
                
                if all_passed:
                    logger.info("✅ Web interface accessibility successful")
                    return True
                else:
                    logger.error("❌ Some web interface elements missing")
                    return False
            else:
                logger.error(f"❌ Web interface not accessible: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"❌ Web interface request failed: {e}")
            return False
    
    def test_configuration_files(self) -> bool:
        """Test configuration files validity"""
        logger.info("⚙️ Testing configuration files...")
        
        config_files = [
            (self.project_root / "config" / "api_config.json", "API configuration"),
            (self.project_root / "law-firm-ai" / "local-training" / "training_config.json", "Training configuration"),
            (self.project_root / ".env.template", "Environment template")
        ]
        
        all_valid = True
        
        for file_path, description in config_files:
            if file_path.exists():
                try:
                    if file_path.suffix == '.json':
                        with open(file_path, 'r') as f:
                            json.load(f)  # Validate JSON
                    logger.info(f"   ✅ {description}")
                except json.JSONDecodeError as e:
                    logger.error(f"   ❌ {description}: Invalid JSON - {e}")
                    all_valid = False
                except Exception as e:
                    logger.error(f"   ❌ {description}: Error - {e}")
                    all_valid = False
            else:
                logger.error(f"   ❌ {description}: File not found")
                all_valid = False
        
        if all_valid:
            logger.info("✅ Configuration files validation successful")
            return True
        else:
            logger.error("❌ Some configuration files are invalid")
            return False
    
    def run_performance_test(self) -> bool:
        """Run performance test with multiple requests"""
        logger.info("⚡ Running performance test...")
        
        test_requests = 5
        successful_requests = 0
        total_time = 0
        
        test_prompt = "Erstellen Sie eine kurze rechtliche Antwort auf eine Mahnung."
        
        for i in range(test_requests):
            try:
                start_time = time.time()
                
                payload = {
                    "prompt": test_prompt,
                    "document_type": "general", 
                    "user_id": f"perf_test_user_{i}"
                }
                
                response = requests.post(
                    f"{self.api_base}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                end_time = time.time()
                request_time = end_time - start_time
                total_time += request_time
                
                if response.status_code == 200:
                    successful_requests += 1
                    logger.info(f"   Request {i+1}: ✅ ({request_time:.2f}s)")
                else:
                    logger.error(f"   Request {i+1}: ❌ ({response.status_code})")
                    
            except Exception as e:
                logger.error(f"   Request {i+1}: ❌ ({e})")
        
        success_rate = (successful_requests / test_requests) * 100
        avg_time = total_time / test_requests if test_requests > 0 else 0
        
        logger.info(f"   Success rate: {success_rate:.1f}% ({successful_requests}/{test_requests})")
        logger.info(f"   Average response time: {avg_time:.2f}s")
        
        if success_rate >= 80 and avg_time <= 30:
            logger.info("✅ Performance test successful")
            return True
        else:
            logger.error("❌ Performance test failed (success rate < 80% or avg time > 30s)")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all tests and return results"""
        self.print_test_banner()
        
        tests = [
            ("API Health Check", self.test_api_health),
            ("Document Generation", self.test_document_generation),
            ("Feedback Submission", self.test_feedback_submission),
            ("Improvement Feedback", self.test_improvement_feedback),
            ("Metrics Collection", self.test_metrics_collection),
            ("Database Operations", self.test_database_operations),
            ("Training System Readiness", self.test_training_readiness),
            ("Web Interface Accessibility", self.test_web_interface_accessibility),
            ("Configuration Files", self.test_configuration_files),
            ("Performance Test", self.run_performance_test)
        ]
        
        results = {}
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running: {test_name}")
            logger.info('='*60)
            
            try:
                start_time = time.time()
                result = test_func()
                end_time = time.time()
                
                results[test_name] = {
                    'passed': result,
                    'duration': end_time - start_time
                }
                
                if result:
                    passed_tests += 1
                    
            except Exception as e:
                logger.error(f"❌ Test '{test_name}' crashed: {e}")
                results[test_name] = {
                    'passed': False,
                    'duration': 0,
                    'error': str(e)
                }
        
        # Print summary
        self.print_test_summary(results, passed_tests, total_tests)
        
        return results
    
    def print_test_summary(self, results: Dict, passed: int, total: int):
        """Print test summary"""
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                         TEST SUMMARY                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 Results: {passed}/{total} tests passed ({success_rate:.1f}%)                    ║
║                                                              ║
║  📋 Test Details:                                           ║
"""
        
        for test_name, result in results.items():
            status = "✅" if result['passed'] else "❌"
            duration = result['duration']
            summary += f"║    {status} {test_name:<40} ({duration:.2f}s)     ║\n"
        
        summary += "║                                                              ║\n"
        
        if success_rate >= 80:
            summary += "║  🎉 SYSTEM STATUS: READY FOR PRODUCTION! 🎉               ║\n"
        elif success_rate >= 60:
            summary += "║  ⚠️  SYSTEM STATUS: PARTIALLY FUNCTIONAL                   ║\n"
        else:
            summary += "║  🚨 SYSTEM STATUS: NEEDS ATTENTION                       ║\n"
        
        summary += "║                                                              ║\n"
        summary += f"║  📅 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                   ║\n"
        summary += "╚══════════════════════════════════════════════════════════════╝"
        
        print(summary)
        
        # Save results to file
        results_file = self.project_root / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'passed': passed,
                    'total': total,
                    'success_rate': success_rate
                },
                'results': results
            }, f, indent=2)
        
        logger.info(f"\n📄 Test results saved to: {results_file}")

if __name__ == "__main__":
    import sys
    
    tester = IntelligentSystemTester()
    results = tester.run_all_tests()
    
    # Determine exit code
    passed_tests = sum(1 for r in results.values() if r['passed'])
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    if success_rate >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure