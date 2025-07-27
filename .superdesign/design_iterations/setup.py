#!/usr/bin/env python3
"""
BMAD Scrum Master Agent Setup Script
Advanced Scrum Master AI Agent for BMAD-METHOD Framework
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("BMAD_SCRUM_MASTER_DOCUMENTATION.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    requirements = []
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements

# Package metadata
setup(
    name="bmad-scrum-master",
    version="1.0.0",
    author="BMAD-METHOD Framework Team",
    author_email="team@bmad-method.com",
    description="Advanced Scrum Master AI Agent for BMAD-METHOD Framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/bmad-method/scrum-master",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Core dependencies
        "asyncio>=3.4.3",
        "aiohttp>=3.8.0",
        "aiofiles>=0.8.0",
        "pydantic>=1.10.0",
        "sqlalchemy>=1.4.0",
        "redis>=4.3.0",
        "python-dateutil>=2.8.0",
        "requests>=2.28.0",
        "fastapi>=0.85.0",
        "uvicorn>=0.18.0",
        "python-dotenv>=0.19.0",
        "structlog>=22.1.0",
        
        # Data science
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        
        # Security
        "cryptography>=3.4.0",
        "python-jose[cryptography]>=3.3.0",
        
        # External integrations
        "jira>=3.4.0",
        "slack-sdk>=3.18.0",
        "PyGithub>=1.55.0",
        
        # Cloud services
        "boto3>=1.24.0",
        
        # CLI
        "click>=8.1.0",
        "rich>=12.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.1.0",
            "pytest-asyncio>=0.19.0",
            "pytest-cov>=3.0.0",
            "black>=22.6.0",
            "flake8>=5.0.0",
            "mypy>=0.971",
            "isort>=5.10.0",
            "pre-commit>=2.20.0",
        ],
        "ai": [
            "tensorflow>=2.9.0",
            "torch>=1.12.0",
            "transformers>=4.21.0",
            "spacy>=3.4.0",
            "nltk>=3.7.0",
        ],
        "azure": [
            "azure-devops>=6.0.0",
            "azure-storage-blob>=12.12.0",
        ],
        "aws": [
            "boto3>=1.24.0",
            "botocore>=1.27.0",
        ],
        "gcp": [
            "google-cloud-storage>=2.5.0",
            "google-api-python-client>=2.65.0",
        ],
        "monitoring": [
            "prometheus-client>=0.14.0",
            "sentry-sdk>=1.9.0",
            "datadog>=0.44.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.10.0",
        ],
        "all": [
            # Development tools
            "pytest>=7.1.0",
            "pytest-asyncio>=0.19.0",
            "pytest-cov>=3.0.0",
            "black>=22.6.0",
            "flake8>=5.0.0",
            "mypy>=0.971",
            "isort>=5.10.0",
            "pre-commit>=2.20.0",
            
            # AI/ML
            "tensorflow>=2.9.0",
            "torch>=1.12.0",
            "transformers>=4.21.0",
            "spacy>=3.4.0",
            "nltk>=3.7.0",
            
            # Cloud platforms
            "azure-devops>=6.0.0",
            "azure-storage-blob>=12.12.0",
            "boto3>=1.24.0",
            "google-cloud-storage>=2.5.0",
            
            # Monitoring
            "prometheus-client>=0.14.0",
            "sentry-sdk>=1.9.0",
            "datadog>=0.44.0",
            
            # Visualization
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.10.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "bmad-scrum-master=bmad_scrum_master.cli:main",
            "bmad-sm=bmad_scrum_master.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "bmad_scrum_master": [
            "templates/*.html",
            "templates/*.json",
            "static/*.css",
            "static/*.js",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/bmad-method/scrum-master/issues",
        "Source": "https://github.com/bmad-method/scrum-master",
        "Documentation": "https://bmad-method.com/docs/scrum-master",
        "Homepage": "https://bmad-method.com",
    },
    keywords=[
        "scrum", "agile", "project-management", "ai", "automation",
        "bmad-method", "sprint-planning", "velocity-tracking",
        "team-coordination", "quality-assurance", "risk-management"
    ],
)