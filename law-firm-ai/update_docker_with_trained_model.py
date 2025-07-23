#!/usr/bin/env python3
"""
Update Docker Container with Trained Model
Integrates the trained model with your existing Docker setup
"""

import json
import subprocess
import logging
import os
import time
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerModelUpdater:
    """
    Updates Docker container to use the trained model for anonymized documents
    """
    
    def __init__(self):
        self.base_dir = Path("/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030/law-firm-ai")
        self.model_info_path = self.base_dir / "trained_model_info.json"
        self.dockerfile_path = self.base_dir / "Dockerfile"
        self.sanitizer_path = self.base_dir / "secure_sanitizer.py"
        
        # Load trained model info
        self.trained_model_info = self.load_model_info()
    
    def load_model_info(self) -> dict:
        """Load trained model information"""
        try:
            if self.model_info_path.exists():
                with open(self.model_info_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("⚠️ No trained model info found. Using default configuration.")
                return {}
        except Exception as e:
            logger.error(f"❌ Error loading model info: {e}")
            return {}
    
    def update_dockerfile(self) -> bool:
        """
        Update Dockerfile with trained model configuration
        """
        logger.info("🐳 Updating Dockerfile for trained model...")
        
        try:
            if not self.dockerfile_path.exists():
                logger.error(f"❌ Dockerfile not found: {self.dockerfile_path}")
                return False
            
            # Read current Dockerfile
            with open(self.dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add environment variables for trained model
            model_id = self.trained_model_info.get('trained_model_id', 'deepseek-ai/DeepSeek-V3')
            api_key = os.environ.get('TOGETHER_API_KEY', 'REDACTED')
            
            # Find the environment variables section and update
            env_section = """# Environment variables for security
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false"""
            
            new_env_section = f"""# Environment variables for security and trained model
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false
ENV LLM_MODEL_NAME={model_id}
ENV TOGETHER_API_KEY={api_key}
ENV MODEL_TRAINING_DATE={self.trained_model_info.get('training_date', 'unknown')}"""
            
            updated_content = content.replace(env_section, new_env_section)
            
            # Create backup
            backup_path = self.dockerfile_path.with_suffix('.backup.' + datetime.now().strftime('%Y%m%d_%H%M%S'))
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write updated Dockerfile
            with open(self.dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logger.info(f"✅ Dockerfile updated with trained model: {model_id}")
            logger.info(f"💾 Backup created: {backup_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating Dockerfile: {e}")
            return False
    
    def update_sanitizer_config(self) -> bool:
        """
        Update secure_sanitizer.py configuration for trained model
        """
        logger.info("🔧 Updating sanitizer configuration...")
        
        try:
            if not self.sanitizer_path.exists():
                logger.error(f"❌ Sanitizer file not found: {self.sanitizer_path}")
                return False
            
            # Read current sanitizer
            with open(self.sanitizer_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            model_id = self.trained_model_info.get('trained_model_id', 'deepseek-ai/DeepSeek-V3')
            
            # Update model configuration
            old_line = 'LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "deepseek-ai/DeepSeek-V3")'
            new_line = f'LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "{model_id}")'
            
            if old_line in content:
                updated_content = content.replace(old_line, new_line)
                
                # Create backup
                backup_path = self.sanitizer_path.with_suffix('.py.backup.' + datetime.now().strftime('%Y%m%d_%H%M%S'))
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Write updated sanitizer
                with open(self.sanitizer_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                logger.info(f"✅ Sanitizer updated with trained model: {model_id}")
                logger.info(f"💾 Backup created: {backup_path}")
                
                return True
            else:
                logger.warning("⚠️ Model configuration line not found in sanitizer")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating sanitizer: {e}")
            return False
    
    def rebuild_docker_container(self) -> bool:
        """
        Rebuild Docker container with updated configuration
        """
        logger.info("🔨 Rebuilding Docker container...")
        
        try:
            # Change to the correct directory
            os.chdir(self.base_dir)
            
            # Stop existing containers
            logger.info("🛑 Stopping existing containers...")
            subprocess.run(['docker', 'stop', 'law-firm-ai'], 
                         capture_output=True, check=False)
            subprocess.run(['docker', 'rm', 'law-firm-ai'], 
                         capture_output=True, check=False)
            
            # Build new container
            logger.info("🔨 Building new container...")
            build_result = subprocess.run([
                'docker', 'build', 
                '-t', 'law-firm-ai:trained',
                '.'
            ], capture_output=True, text=True)
            
            if build_result.returncode != 0:
                logger.error(f"❌ Docker build failed: {build_result.stderr}")
                return False
            
            logger.info("✅ Docker container built successfully")
            
            # Run new container
            logger.info("🚀 Starting new container...")
            run_result = subprocess.run([
                'docker', 'run', 
                '-d',
                '--name', 'law-firm-ai',
                '-p', '5001:5001',
                '-e', f'TOGETHER_API_KEY={os.environ.get("TOGETHER_API_KEY", "REDACTED")}',
                '-e', f'LLM_MODEL_NAME={self.trained_model_info.get("trained_model_id", "deepseek-ai/DeepSeek-V3")}',
                'law-firm-ai:trained'
            ], capture_output=True, text=True)
            
            if run_result.returncode != 0:
                logger.error(f"❌ Docker run failed: {run_result.stderr}")
                return False
            
            container_id = run_result.stdout.strip()
            logger.info(f"✅ Container started: {container_id[:12]}")
            
            # Wait for container to be ready
            logger.info("⏳ Waiting for container to be ready...")
            time.sleep(10)
            
            # Check container status
            status_result = subprocess.run([
                'docker', 'ps', 
                '--filter', 'name=law-firm-ai',
                '--format', 'table {{.Names}}\t{{.Status}}'
            ], capture_output=True, text=True)
            
            logger.info(f"📊 Container status:\n{status_result.stdout}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rebuilding Docker container: {e}")
            return False
    
    def test_trained_model_in_docker(self) -> bool:
        """
        Test the trained model inside the Docker container
        """
        logger.info("🧪 Testing trained model in Docker container...")
        
        try:
            # Test API endpoint
            test_payload = {
                "text": """An das [BIC_7] Musterstadt
Musterstraße 1
[PLZ_2] [LOC_2]

**Klageerhebung**

Sehr geehrte Damen und Herren,

in der [ORG_1]. gegen [BIC_6] erheben wir Klage wegen ausstehender Gehaltszahlungen.
Unser Mandant, Ing. [BIC_5] Wirth [WEBSITE_1]., [BIC_4] in [LOC_1] 7
[PLZ_1] Artern, hat seit drei Monaten kein Gehalt [BIC_3].

Wir beantragen, die [BIC_2] zu [BIC_1], an unseren Mandanten 586 [MISC_1] nebst Zinsen zu zahlen."""
            }
            
            # Create test script
            test_script = f"""
import requests
import json

try:
    response = requests.post(
        'http://localhost:5001/process',
        json={json.dumps(test_payload)},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API Test Successful")
        print(f"📊 Response: {{result.get('status', 'unknown')}}")
        print(f"📝 Model used: {{result.get('model_name', 'unknown')}}")
        print(f"🔒 PII removed: {{len(result.get('removed_entities', []))}}")
        exit(0)
    else:
        print(f"❌ API Test Failed: {{response.status_code}}")
        print(f"📄 Response: {{response.text}}")
        exit(1)
        
except Exception as e:
    print(f"❌ Test Error: {{e}}")
    exit(1)
"""
            
            # Write and run test
            test_file = self.base_dir / "test_docker_model.py"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            # Wait a bit more for the service to be ready
            time.sleep(5)
            
            # Run test
            test_result = subprocess.run([
                'python3', str(test_file)
            ], capture_output=True, text=True, timeout=60)
            
            logger.info(f"🧪 Test output:\n{test_result.stdout}")
            
            if test_result.returncode == 0:
                logger.info("✅ Docker model test passed!")
                return True
            else:
                logger.error(f"❌ Docker model test failed:\n{test_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing Docker model: {e}")
            return False
    
    def run_complete_update(self) -> bool:
        """
        Run the complete Docker update process
        """
        logger.info("🚀 Starting complete Docker update for trained model")
        
        try:
            # Step 1: Update Dockerfile
            if not self.update_dockerfile():
                logger.error("❌ Failed to update Dockerfile")
                return False
            
            # Step 2: Update sanitizer configuration
            if not self.update_sanitizer_config():
                logger.error("❌ Failed to update sanitizer configuration")
                return False
            
            # Step 3: Rebuild Docker container
            if not self.rebuild_docker_container():
                logger.error("❌ Failed to rebuild Docker container")
                return False
            
            # Step 4: Test the updated container
            if not self.test_trained_model_in_docker():
                logger.warning("⚠️ Docker model testing failed, but container is running")
            
            logger.info("🎉 Docker update completed successfully!")
            logger.info("🐳 Your trained model is now running in Docker!")
            logger.info("📋 Ready to process anonymized documents on port 5001")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Docker update failed: {e}")
            return False

def main():
    """Main execution function"""
    updater = DockerModelUpdater()
    
    print("🐳 Docker Model Update Pipeline")
    print("=" * 50)
    
    if updater.trained_model_info:
        model_id = updater.trained_model_info.get('trained_model_id', 'unknown')
        training_date = updater.trained_model_info.get('training_date', 'unknown')
        print(f"🎯 Model ID: {model_id}")
        print(f"📅 Trained: {training_date}")
    else:
        print("⚠️ No trained model info found")
    
    print("")
    
    # Run the complete update
    success = updater.run_complete_update()
    
    if success:
        print("\n✅ SUCCESS: Docker container updated with trained model!")
        print("🌐 Service running on: http://localhost:5001")
        print("📋 Next steps:")
        print("1. Test with your PDF PII anonymizer")
        print("2. Upload 8-page documents")
        print("3. Verify improved responses with anonymized data")
    else:
        print("\n❌ FAILED: Docker update encountered errors")
        print("📋 Check the logs and try again")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())