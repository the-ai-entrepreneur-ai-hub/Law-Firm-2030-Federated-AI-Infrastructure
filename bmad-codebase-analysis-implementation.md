# BMAD Codebase Analysis Agent - Implementation Guide

## Overview

This document provides practical examples and implementation guidance for the BMAD Codebase Analysis Agent. It demonstrates how to integrate the agent into development workflows and use it for comprehensive codebase analysis.

## Quick Start Examples

### 1. CLI Integration

```bash
# Initialize BMAD Codebase Analysis for a project
bmad-codebase init --project "law-firm-2030" --path "/path/to/codebase"

# Perform comprehensive analysis
bmad-codebase analyze --path "/path/to/codebase" --output "./analysis/"

# Generate flattened codebase for AI consumption
bmad-codebase flatten --path "/path/to/codebase" --format json --output "./flattened.json"

# Analyze specific components
bmad-codebase analyze --path "/path/to/codebase" --include "**/*.py,**/*.js" --exclude "**/venv/**,**/node_modules/**"

# Generate migration assessment
bmad-codebase migrate --path "/path/to/codebase" --target "microservices" --output "./migration-plan.md"

# Security and quality analysis
bmad-codebase audit --path "/path/to/codebase" --include-security --include-quality --output "./audit-report.json"

# Dependency analysis
bmad-codebase dependencies --path "/path/to/codebase" --check-vulnerabilities --output "./dependencies.json"
```

### 2. Node.js SDK Integration

```javascript
// Installation: npm install @bmad/codebase-analysis

const { BMadCodebaseAnalyzer } = require('@bmad/codebase-analysis');

const analyzer = new BMadCodebaseAnalyzer({
  apiKey: process.env.BMAD_API_KEY,
  environment: 'production'
});

// Comprehensive codebase analysis
async function analyzeCodebase() {
  const analysisConfig = {
    source: {
      type: 'local_path',
      path: '/path/to/law-firm-2030'
    },
    analysisScope: {
      includePatterns: ['**/*.py', '**/*.js', '**/*.html', '**/*.json', '**/*.yaml'],
      excludePatterns: ['**/venv/**', '**/node_modules/**', '**/__pycache__/**'],
      binaryHandling: 'exclude',
      maxFileSize: '10MB'
    },
    outputFormat: {
      structure: 'json',
      includeContent: true,
      includeMetadata: true,
      compression: 'gzip'
    },
    analysisDepth: {
      structureAnalysis: true,
      dependencyAnalysis: true,
      qualityAssessment: true,
      securityScan: true,
      performanceAnalysis: true
    }
  };

  try {
    const analysis = await analyzer.analyzeCodebase(analysisConfig);
    
    console.log('Analysis Summary:', analysis.analysisSummary);
    console.log('Quality Score:', analysis.qualityAssessment.codeMetrics.overallScore);
    console.log('Security Issues:', analysis.qualityAssessment.securityIssues.length);
    
    // Save comprehensive analysis
    await analyzer.saveAnalysis(analysis, './analysis-output/');
    
    // Generate flattened representation for AI consumption
    const flattened = await analyzer.flattenCodebase(analysis);
    await analyzer.saveFlattened(flattened, './flattened-codebase.json');
    
    // Generate documentation
    const docs = await analyzer.generateDocumentation(analysis);
    await analyzer.saveDocumentation(docs, './documentation/');
    
    return analysis;
  } catch (error) {
    console.error('Analysis failed:', error);
  }
}

// Migration planning example
async function generateMigrationPlan() {
  const migrationConfig = {
    source: '/path/to/legacy-codebase',
    target: {
      architecture: 'microservices',
      framework: 'modern-stack',
      cloudProvider: 'aws'
    },
    constraints: {
      timeline: '6 months',
      budget: 500000,
      riskTolerance: 'medium'
    }
  };

  const migrationPlan = await analyzer.generateMigrationPlan(migrationConfig);
  
  console.log('Migration Phases:', migrationPlan.phases.length);
  console.log('Estimated Effort:', migrationPlan.effortEstimate);
  console.log('Risk Assessment:', migrationPlan.riskAssessment);
  
  return migrationPlan;
}
```

### 3. Python SDK Integration

```python
# Installation: pip install bmad-codebase-analysis

from bmad_codebase_analysis import BMadCodebaseAnalyzer
import asyncio

analyzer = BMadCodebaseAnalyzer(
    api_key=os.getenv('BMAD_API_KEY'),
    environment='production'
)

async def analyze_legal_platform():
    """Analyze the legal platform codebase"""
    
    config = {
        'source': {
            'type': 'local_path',
            'path': '/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030'
        },
        'analysis_scope': {
            'include_patterns': [
                '**/*.py', '**/*.js', '**/*.html', '**/*.json', 
                '**/*.yaml', '**/*.md', '**/*.dockerfile', '**/*.sh'
            ],
            'exclude_patterns': [
                '**/venv/**', '**/pii_env/**', '**/venv_new/**',
                '**/__pycache__/**', '**/node_modules/**',
                '**/*.pyc', '**/*.log'
            ],
            'binary_handling': 'include_selective',
            'max_file_size': '10MB'
        },
        'output_format': {
            'structure': 'json',
            'include_content': True,
            'include_metadata': True
        },
        'analysis_depth': {
            'structure_analysis': True,
            'dependency_analysis': True,
            'quality_assessment': True,
            'security_scan': True,
            'performance_analysis': True
        }
    }
    
    try:
        # Perform comprehensive analysis
        analysis = await analyzer.analyze_codebase(config)
        
        # Extract key insights
        summary = analysis['analysis_summary']
        print(f"Project Type: {summary['project_type']}")
        print(f"Languages: {', '.join(summary['languages'])}")
        print(f"Frameworks: {', '.join(summary['frameworks'])}")
        print(f"Total Files: {summary['total_files']}")
        print(f"Quality Score: {summary['quality_score']}/100")
        
        # Analyze dependencies
        deps = analysis['dependency_analysis']
        print(f"External Dependencies: {len(deps['external'])}")
        print(f"Dependency Vulnerabilities: {len(deps['vulnerabilities'])}")
        
        # Quality assessment
        quality = analysis['quality_assessment']
        print(f"Technical Debt Score: {quality['technical_debt']['score']}")
        print(f"Code Smells: {len(quality['code_smells'])}")
        
        # Generate AI-consumable format
        flattened = await analyzer.flatten_for_ai(analysis)
        
        # Save results
        await analyzer.save_analysis(analysis, './analysis_output/')
        await analyzer.save_flattened(flattened, './law_firm_flattened.json')
        
        return analysis
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return None

# Example: Security-focused analysis
async def security_audit():
    """Perform security-focused analysis"""
    
    config = {
        'source': {
            'type': 'local_path',
            'path': '/path/to/codebase'
        },
        'analysis_scope': {
            'security_focus': True,
            'include_patterns': ['**/*.py', '**/*.js', '**/*.yaml', '**/*.json']
        },
        'analysis_depth': {
            'security_scan': True,
            'dependency_vulnerabilities': True,
            'secrets_detection': True,
            'compliance_check': True
        }
    }
    
    security_report = await analyzer.security_audit(config)
    
    print("Security Findings:")
    for finding in security_report['findings']:
        print(f"- {finding['severity']}: {finding['description']}")
    
    return security_report

if __name__ == "__main__":
    asyncio.run(analyze_legal_platform())
```

## Configuration Examples

### 1. Analysis Configuration File

```yaml
# bmad-analysis-config.yaml
analysis:
  project:
    name: "Law Firm Vision 2030"
    type: "ai-legal-platform"
    version: "2.0"
    
  source:
    type: "local_path"
    path: "/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030"
    
  scope:
    include_patterns:
      - "**/*.py"
      - "**/*.js"
      - "**/*.html"
      - "**/*.json"
      - "**/*.yaml"
      - "**/*.md"
      - "**/Dockerfile*"
      - "**/*.sh"
      - "**/*.bat"
    exclude_patterns:
      - "**/venv/**"
      - "**/pii_env/**"
      - "**/venv_new/**"
      - "**/__pycache__/**"
      - "**/node_modules/**"
      - "**/*.pyc"
      - "**/*.log"
      - "**/dist/**"
      - "**/build/**"
    binary_handling: "include_selective"
    max_file_size: "10MB"
    
  analysis_depth:
    structure_analysis: true
    dependency_analysis: true
    quality_assessment: true
    security_scan: true
    performance_analysis: true
    documentation_extraction: true
    
  output:
    format: "json"
    include_content: true
    include_metadata: true
    compression: "gzip"
    destinations:
      - "./analysis_output/"
      - "./flattened_output/"
      
  quality_thresholds:
    minimum_quality_score: 70
    maximum_complexity: 15
    minimum_test_coverage: 80
    
  security:
    check_vulnerabilities: true
    detect_secrets: true
    compliance_standards:
      - "OWASP"
      - "GDPR"
      - "SOC2"
```

### 2. Framework-Specific Analysis

```yaml
# Python/Flask Project Analysis
python_analysis:
  language_specific:
    python:
      check_pep8: true
      analyze_imports: true
      detect_circular_imports: true
      check_requirements: true
      virtual_env_analysis: true
  frameworks:
    flask:
      analyze_routes: true
      check_security: true
      analyze_templates: true
    
# JavaScript/Node.js Project Analysis  
javascript_analysis:
  language_specific:
    javascript:
      check_eslint: true
      analyze_modules: true
      check_package_json: true
      dependency_tree: true
  frameworks:
    express:
      analyze_routes: true
      middleware_analysis: true
    react:
      component_analysis: true
      hook_usage: true
      
# Docker Analysis
docker_analysis:
  containers:
    analyze_dockerfiles: true
    security_scan: true
    layer_optimization: true
    compose_analysis: true
```

## Advanced Usage Patterns

### 1. Multi-Repository Analysis

```javascript
// Analyze multiple related repositories
async function analyzeMultiRepo() {
  const repositories = [
    '/path/to/law-firm-ai',
    '/path/to/law-firm-uploader', 
    '/path/to/law-firm-docs'
  ];
  
  const analyses = [];
  
  for (const repo of repositories) {
    const analysis = await analyzer.analyzeCodebase({
      source: { type: 'local_path', path: repo },
      analysisScope: { /* standard config */ }
    });
    analyses.push(analysis);
  }
  
  // Cross-repository analysis
  const crossAnalysis = await analyzer.analyzeCrossRepository(analyses);
  
  console.log('Shared Dependencies:', crossAnalysis.sharedDependencies);
  console.log('Integration Points:', crossAnalysis.integrationPoints);
  console.log('Consistency Issues:', crossAnalysis.consistencyIssues);
  
  return crossAnalysis;
}
```

### 2. Incremental Analysis

```javascript
// Analyze only changed files since last analysis
async function incrementalAnalysis() {
  const lastAnalysisTimestamp = '2024-01-15T10:00:00Z';
  
  const config = {
    source: { type: 'local_path', path: '/path/to/codebase' },
    incremental: {
      enabled: true,
      since: lastAnalysisTimestamp,
      changedFilesOnly: true
    }
  };
  
  const incrementalResult = await analyzer.analyzeIncremental(config);
  
  console.log('Changed Files:', incrementalResult.changedFiles.length);
  console.log('Impact Analysis:', incrementalResult.impactAnalysis);
  
  return incrementalResult;
}
```

### 3. Custom Pattern Detection

```javascript
// Define custom patterns for analysis
async function customPatternAnalysis() {
  const customPatterns = {
    antiPatterns: [
      {
        name: 'Hardcoded Secrets',
        pattern: /(?:password|secret|key|token)\s*=\s*["'][^"']+["']/gi,
        severity: 'high',
        description: 'Hardcoded secrets detected'
      },
      {
        name: 'SQL Injection Risk',
        pattern: /execute\s*\(\s*["'].*%s.*["']/gi,
        severity: 'critical',
        description: 'Potential SQL injection vulnerability'
      }
    ],
    bestPractices: [
      {
        name: 'Proper Error Handling',
        pattern: /try\s*:\s*.*\s*except\s*Exception/gi,
        severity: 'medium',
        description: 'Generic exception handling'
      }
    ]
  };
  
  const analysis = await analyzer.analyzeWithCustomPatterns({
    source: { type: 'local_path', path: '/path/to/codebase' },
    customPatterns: customPatterns
  });
  
  return analysis;
}
```

## Integration with CI/CD

### 1. GitHub Actions Integration

```yaml
# .github/workflows/bmad-codebase-analysis.yml
name: BMAD Codebase Analysis

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for analysis
          
      - name: Setup BMAD CLI
        run: |
          curl -L https://github.com/bmad/cli/releases/latest/download/bmad-linux-amd64 -o bmad
          chmod +x bmad
          sudo mv bmad /usr/local/bin/
          
      - name: Run Codebase Analysis
        run: |
          bmad-codebase analyze \
            --path . \
            --config .bmad/analysis-config.yaml \
            --output ./analysis/ \
            --format json
            
      - name: Security Audit
        run: |
          bmad-codebase audit \
            --path . \
            --security-focus \
            --output ./security-audit.json
            
      - name: Quality Gate Check
        run: |
          bmad-codebase quality-gate \
            --analysis ./analysis/ \
            --min-quality-score 70 \
            --max-security-issues 0
            
      - name: Generate Flattened Codebase
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          bmad-codebase flatten \
            --path . \
            --output ./flattened-codebase.json \
            --optimize-for-ai
            
      - name: Upload Analysis Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: bmad-analysis
          path: |
            ./analysis/
            ./security-audit.json
            ./flattened-codebase.json
            
      - name: Comment PR with Results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const analysis = JSON.parse(fs.readFileSync('./analysis/summary.json', 'utf8'));
            
            const comment = `
            ## 📊 BMAD Codebase Analysis Results
            
            **Quality Score:** ${analysis.qualityScore}/100
            **Languages:** ${analysis.languages.join(', ')}
            **Total Files:** ${analysis.totalFiles}
            **Security Issues:** ${analysis.securityIssues}
            
            ### Key Findings:
            ${analysis.keyFindings.map(finding => `- ${finding}`).join('\n')}
            
            [View Full Report](./analysis/)
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 2. Jenkins Pipeline Integration

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        BMAD_API_KEY = credentials('bmad-api-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('BMAD Codebase Analysis') {
            steps {
                script {
                    sh '''
                        # Install BMAD CLI
                        curl -L https://github.com/bmad/cli/releases/latest/download/bmad-linux-amd64 -o bmad
                        chmod +x bmad
                        
                        # Run comprehensive analysis
                        ./bmad codebase analyze --path . --output ./analysis/
                        
                        # Generate reports
                        ./bmad codebase report --analysis ./analysis/ --format html --output ./reports/
                    '''
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    def analysis = readJSON file: './analysis/summary.json'
                    
                    if (analysis.qualityScore < 70) {
                        error("Quality score ${analysis.qualityScore} below threshold of 70")
                    }
                    
                    if (analysis.securityIssues > 0) {
                        error("${analysis.securityIssues} security issues found")
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'analysis/**, reports/**', fingerprint: true
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'index.html',
                    reportName: 'BMAD Analysis Report'
                ])
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

## Real-World Example: Law Firm Platform Analysis

```python
# Comprehensive analysis of the Law Firm Vision 2030 project
async def analyze_law_firm_platform():
    """
    Real-world example analyzing the current Law Firm Vision 2030 codebase
    """
    
    config = {
        'source': {
            'type': 'local_path',
            'path': '/mnt/c/Users/Administrator/serveless-apps/Law Firm Vision 2030'
        },
        'analysis_scope': {
            'include_patterns': [
                '**/*.py',     # Python AI/ML code
                '**/*.js',     # JavaScript for web interfaces
                '**/*.html',   # Web templates
                '**/*.json',   # Configuration and data files
                '**/*.yaml',   # Docker and config files
                '**/*.md',     # Documentation
                '**/Dockerfile*',    # Container definitions
                '**/*.sh',     # Shell scripts
                '**/*.bat',    # Windows batch files
            ],
            'exclude_patterns': [
                '**/venv/**',        # Python virtual environments
                '**/pii_env/**',     # Specific virtual env
                '**/venv_new/**',    # Additional virtual env
                '**/__pycache__/**', # Python cache
                '**/node_modules/**', # Node.js dependencies
                '**/*.pyc',          # Compiled Python
                '**/*.log',          # Log files
                '**/site-packages/**' # Python packages
            ],
            'binary_handling': 'include_selective',
            'max_file_size': '10MB'
        },
        'analysis_depth': {
            'structure_analysis': True,
            'dependency_analysis': True,
            'quality_assessment': True,
            'security_scan': True,
            'performance_analysis': True,
            'ai_ml_analysis': True,      # Special AI/ML code analysis
            'docker_analysis': True,     # Container analysis
            'compliance_check': True     # GDPR/legal compliance
        },
        'legal_specific': {
            'pii_detection': True,
            'gdpr_compliance': True,
            'attorney_client_privilege': True,
            'data_residency': True
        }
    }
    
    # Perform analysis
    analysis = await analyzer.analyze_codebase(config)
    
    # Extract insights specific to legal AI platform
    legal_insights = {
        'ai_components': [],
        'pii_handling': [],
        'security_measures': [],
        'compliance_status': {},
        'architecture_patterns': []
    }
    
    # Analyze AI/ML components
    for component in analysis['structure_representation']['components']:
        if 'ai' in component['name'].lower() or 'model' in component['name'].lower():
            legal_insights['ai_components'].append({
                'name': component['name'],
                'type': component['type'],
                'complexity': component['metrics']['complexity'],
                'dependencies': component['dependencies']
            })
    
    # Analyze PII handling
    pii_patterns = [
        'pii', 'anonymize', 'sanitize', 'redact', 'mask'
    ]
    
    for file_analysis in analysis['file_analyses']:
        for pattern in pii_patterns:
            if pattern in file_analysis['content'].lower():
                legal_insights['pii_handling'].append({
                    'file': file_analysis['path'],
                    'pattern': pattern,
                    'line_count': file_analysis['content'].lower().count(pattern)
                })
    
    # Security analysis specific to legal requirements
    security_assessment = {
        'encryption_usage': 0,
        'authentication_methods': [],
        'data_protection_measures': [],
        'audit_logging': 0
    }
    
    # Generate recommendations
    recommendations = await analyzer.generate_legal_recommendations(analysis)
    
    # Create comprehensive report
    report = {
        'executive_summary': {
            'project_type': 'AI-Powered Legal Platform',
            'architecture': 'Federated AI with Local PII Processing',
            'quality_score': analysis['quality_assessment']['overall_score'],
            'security_score': analysis['security_assessment']['score'],
            'compliance_score': analysis['compliance_assessment']['score']
        },
        'technical_analysis': analysis,
        'legal_insights': legal_insights,
        'security_assessment': security_assessment,
        'recommendations': recommendations,
        'migration_roadmap': await analyzer.generate_migration_roadmap(analysis)
    }
    
    # Save results
    await analyzer.save_analysis(report, './law_firm_analysis/')
    
    # Generate AI-consumable format for other BMAD agents
    flattened = await analyzer.flatten_for_bmad_consumption(analysis)
    await analyzer.save_flattened(flattened, './law_firm_flattened.json')
    
    return report

# Usage
if __name__ == "__main__":
    report = asyncio.run(analyze_law_firm_platform())
    
    print("=== Law Firm Platform Analysis Report ===")
    print(f"Quality Score: {report['executive_summary']['quality_score']}/100")
    print(f"Security Score: {report['executive_summary']['security_score']}/100")
    print(f"Compliance Score: {report['executive_summary']['compliance_score']}/100")
    print(f"AI Components Found: {len(report['legal_insights']['ai_components'])}")
    print(f"PII Handling Instances: {len(report['legal_insights']['pii_handling'])}")
    print("\nTop Recommendations:")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"{i}. {rec['title']}: {rec['description']}")
```

This implementation guide provides practical examples for integrating and using the BMAD Codebase Analysis Agent in real-world scenarios, with specific focus on the legal AI platform use case while maintaining broad applicability across different project types and development workflows.