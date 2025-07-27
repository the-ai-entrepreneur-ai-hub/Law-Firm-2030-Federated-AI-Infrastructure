# BMAD Architectural Design Agent - Usage Examples

## Overview

This document provides practical examples of how the BMAD Architectural Design Agent integrates into real development workflows, showing specific commands, inputs, and expected outputs for various scenarios.

## Usage Patterns

### 1. CLI Integration Example

```bash
# Initialize BMAD Agent for a new project
bmad-arch init --project "legal-platform" --domain "legal-tech"

# Analyze existing architecture
bmad-arch analyze --input requirements.yaml --existing-system ./current-architecture

# Generate architecture from requirements
bmad-arch design --requirements ./requirements.yaml --output ./architecture/

# Validate proposed architecture
bmad-arch validate --architecture ./architecture/system-design.yaml

# Generate implementation roadmap
bmad-arch roadmap --architecture ./architecture/ --timeline 16weeks --budget 2M

# Update architecture based on feedback
bmad-arch update --architecture ./architecture/ --feedback ./review-comments.yaml
```

### 2. API Integration Example

```javascript
// Node.js SDK Integration
const { BMadArchAgent } = require('@bmad/architectural-design');

const agent = new BMadArchAgent({
  apiKey: process.env.BMAD_API_KEY,
  environment: 'production'
});

// Generate architecture from requirements
async function generateArchitecture() {
  const requirements = {
    projectId: 'law-firm-2030',
    functional: [
      'Document processing pipeline',
      'PII detection and anonymization', 
      'Multi-tenant law firm support',
      'Real-time analytics dashboard'
    ],
    nonFunctional: [
      '99.9% uptime SLA',
      'GDPR compliance',
      'Sub-second response times',
      'Support 1000 concurrent users'
    ],
    constraints: {
      budget: 2000000,
      timeline: '16 weeks',
      existingSystems: ['n8n-agents', 'together-ai'],
      compliance: ['GDPR', 'attorney-client-privilege']
    }
  };

  try {
    const architecture = await agent.generateArchitecture(requirements);
    console.log('Generated Architecture:', architecture);
    
    // Save architecture documents
    await agent.saveArchitecture(architecture, './output/');
    
    // Generate diagrams
    const diagrams = await agent.generateDiagrams(architecture);
    await agent.saveDiagrams(diagrams, './output/diagrams/');
    
    return architecture;
  } catch (error) {
    console.error('Architecture generation failed:', error);
  }
}
```

### 3. Configuration File Examples

#### Requirements Specification File
```yaml
# requirements.yaml
project:
  id: "law-firm-2030-v2"
  name: "Enhanced Legal AI Platform"
  description: "Next-generation federated legal AI system"
  domain: "legal-technology"

functional_requirements:
  document_processing:
    - id: FR001
      description: "Process legal documents with PII detection"
      priority: "high"
      acceptance_criteria:
        - "Detect PII with 99.5% accuracy"
        - "Process documents in under 30 seconds"
        - "Support PDF, DOC, TXT formats"
    
  multi_tenancy:
    - id: FR002
      description: "Support multiple law firms with data isolation"
      priority: "critical"
      acceptance_criteria:
        - "Complete data isolation between firms"
        - "Configurable branding per firm"
        - "Role-based access control"
    
  analytics:
    - id: FR003
      description: "Real-time analytics and reporting"
      priority: "medium"
      acceptance_criteria:
        - "Real-time dashboard updates"
        - "Exportable reports"
        - "Historical trend analysis"

non_functional_requirements:
  performance:
    - id: NFR001
      description: "System response time"
      requirement: "95% of requests under 500ms"
      measurement: "p95 response time"
      
  availability:
    - id: NFR002
      description: "System uptime"
      requirement: "99.9% uptime (8.76 hours downtime/year)"
      measurement: "Monthly uptime percentage"
      
  scalability:
    - id: NFR003
      description: "Concurrent user support"
      requirement: "Support 1000 concurrent users"
      measurement: "Load testing validation"
      
  security:
    - id: NFR004
      description: "Data protection"
      requirement: "End-to-end encryption, GDPR compliance"
      measurement: "Security audit compliance"

constraints:
  budget:
    total: 2000000
    breakdown:
      infrastructure: 800000
      development: 1000000
      compliance: 200000
      
  timeline:
    total_duration: "16 weeks"
    milestones:
      mvp: "8 weeks"
      beta: "12 weeks"
      production: "16 weeks"
      
  technology:
    required:
      - "Together.ai integration"
      - "Docker containerization"
      - "Kubernetes orchestration"
    preferred:
      - "React frontend"
      - "Node.js/Python backend"
      - "PostgreSQL database"
    constraints:
      - "No vendor lock-in"
      - "Open source preferred"
      
  compliance:
    - "GDPR (EU General Data Protection Regulation)"
    - "Attorney-client privilege"
    - "ISO 27001"
    - "SOC 2 Type II"

existing_systems:
  - name: "n8n Local Agents"
    description: "Data anonymization agents"
    technology: "Node.js"
    integration_required: true
    
  - name: "Together.ai LLM"
    description: "Central legal LLM"
    technology: "Cloud API"
    integration_required: true
    
  - name: "Basic Web Interface"
    description: "Current user interface"
    technology: "HTML/CSS/JS"
    replacement_planned: true

success_criteria:
  technical:
    - "All functional requirements implemented"
    - "All non-functional requirements met"
    - "Zero critical security vulnerabilities"
    - "Performance benchmarks achieved"
    
  business:
    - "User adoption rate > 80%"
    - "Customer satisfaction > 4.5/5"
    - "Cost per transaction < $0.10"
    - "ROI positive within 12 months"
```

#### Architecture Configuration Template
```yaml
# architecture-config.yaml
architecture:
  style: "microservices"
  patterns:
    - "event-driven"
    - "api-gateway"
    - "circuit-breaker"
    - "cqrs"
    
technology_stack:
  frontend:
    framework: "react"
    version: "18.x"
    additional:
      - "next.js"
      - "typescript"
      - "tailwindcss"
      
  backend:
    primary: "node.js"
    secondary: "python"
    frameworks:
      - "express.js"
      - "fastapi"
      
  database:
    primary: "postgresql"
    cache: "redis"
    search: "elasticsearch"
    
  messaging:
    queue: "apache-kafka"
    cache: "redis"
    
  infrastructure:
    containerization: "docker"
    orchestration: "kubernetes"
    cloud: "multi-cloud"
    
  monitoring:
    metrics: "prometheus"
    visualization: "grafana"
    logging: "elasticsearch"
    tracing: "jaeger"

security:
  authentication: "oauth2"
  authorization: "rbac"
  encryption:
    at_rest: "aes-256"
    in_transit: "tls-1.3"
  secrets_management: "hashicorp-vault"
  
deployment:
  strategy: "blue-green"
  environments: ["dev", "staging", "production"]
  regions: ["us-east-1", "eu-west-1"]
  
quality:
  code_coverage: 90
  performance_budget: "500ms p95"
  security_scans: true
  dependency_checks: true
```

### 4. GitHub Actions Integration

```yaml
# .github/workflows/bmad-architecture.yml
name: BMAD Architecture Validation

on:
  pull_request:
    paths:
      - 'architecture/**'
      - 'requirements.yaml'
  push:
    branches: [main]

jobs:
  validate-architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup BMAD CLI
        run: |
          curl -L https://github.com/bmad/cli/releases/latest/download/bmad-linux-amd64 -o bmad
          chmod +x bmad
          sudo mv bmad /usr/local/bin/
          
      - name: Validate Architecture
        run: |
          bmad-arch validate \
            --architecture ./architecture/ \
            --requirements ./requirements.yaml \
            --output ./validation-report.json
            
      - name: Check Architecture Compliance
        run: |
          bmad-arch compliance-check \
            --architecture ./architecture/ \
            --standards gdpr,iso27001,soc2 \
            --output ./compliance-report.json
            
      - name: Generate Architecture Diff
        if: github.event_name == 'pull_request'
        run: |
          bmad-arch diff \
            --base-ref origin/main \
            --head-ref HEAD \
            --output ./architecture-diff.json
            
      - name: Comment PR with Results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const validation = JSON.parse(fs.readFileSync('./validation-report.json', 'utf8'));
            const compliance = JSON.parse(fs.readFileSync('./compliance-report.json', 'utf8'));
            
            const comment = `
            ## 🏗️ Architecture Validation Results
            
            ### Validation Status: ${validation.status === 'passed' ? '✅ PASSED' : '❌ FAILED'}
            
            **Issues Found:** ${validation.issues.length}
            **Compliance Score:** ${compliance.score}/100
            
            ### Key Findings:
            ${validation.issues.map(issue => `- ${issue.severity}: ${issue.message}`).join('\n')}
            
            ### Compliance Status:
            - GDPR: ${compliance.gdpr.status}
            - ISO 27001: ${compliance.iso27001.status}
            - SOC 2: ${compliance.soc2.status}
            
            [View Full Report](./validation-report.json)
            `;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 5. VS Code Extension Integration

```typescript
// bmad-vscode-extension/src/extension.ts
import * as vscode from 'vscode';
import { BMadArchAgent } from '@bmad/architectural-design';

export function activate(context: vscode.ExtensionContext) {
  // Command to generate architecture
  const generateArchitecture = vscode.commands.registerCommand(
    'bmad.generateArchitecture',
    async () => {
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
      if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder found');
        return;
      }

      // Show input dialog for requirements
      const requirementsFile = await vscode.window.showInputBox({
        prompt: 'Path to requirements file',
        value: './requirements.yaml'
      });

      if (!requirementsFile) return;

      // Show progress
      vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Generating Architecture',
        cancellable: false
      }, async (progress) => {
        try {
          progress.report({ message: 'Analyzing requirements...' });
          
          const agent = new BMadArchAgent();
          const requirements = await agent.loadRequirements(requirementsFile);
          
          progress.report({ message: 'Generating system design...' });
          const architecture = await agent.generateArchitecture(requirements);
          
          progress.report({ message: 'Creating documentation...' });
          await agent.saveArchitecture(architecture, './architecture/');
          
          progress.report({ message: 'Generating diagrams...' });
          const diagrams = await agent.generateDiagrams(architecture);
          await agent.saveDiagrams(diagrams, './architecture/diagrams/');
          
          vscode.window.showInformationMessage(
            'Architecture generated successfully!',
            'Open Architecture'
          ).then(selection => {
            if (selection === 'Open Architecture') {
              vscode.commands.executeCommand(
                'vscode.open',
                vscode.Uri.file('./architecture/system-design.md')
              );
            }
          });
          
        } catch (error) {
          vscode.window.showErrorMessage(`Failed to generate architecture: ${error.message}`);
        }
      });
    }
  );

  // Command to validate current architecture
  const validateArchitecture = vscode.commands.registerCommand(
    'bmad.validateArchitecture',
    async () => {
      const agent = new BMadArchAgent();
      
      try {
        const validation = await agent.validateArchitecture('./architecture/');
        
        // Show validation results in webview
        const panel = vscode.window.createWebviewPanel(
          'bmadValidation',
          'Architecture Validation',
          vscode.ViewColumn.One,
          { enableScripts: true }
        );
        
        panel.webview.html = generateValidationHTML(validation);
        
      } catch (error) {
        vscode.window.showErrorMessage(`Validation failed: ${error.message}`);
      }
    }
  );

  context.subscriptions.push(generateArchitecture, validateArchitecture);
}

function generateValidationHTML(validation: any): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Architecture Validation</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .passed { background-color: #d4edda; color: #155724; }
            .failed { background-color: #f8d7da; color: #721c24; }
            .issue { margin: 5px 0; padding: 5px; border-left: 3px solid #ffc107; }
        </style>
    </head>
    <body>
        <h1>Architecture Validation Results</h1>
        <div class="status ${validation.status}">
            Status: ${validation.status.toUpperCase()}
        </div>
        
        <h2>Issues Found (${validation.issues.length})</h2>
        ${validation.issues.map(issue => `
            <div class="issue">
                <strong>${issue.severity}:</strong> ${issue.message}
                <br><small>Component: ${issue.component}</small>
            </div>
        `).join('')}
        
        <h2>Compliance Scores</h2>
        <ul>
            <li>GDPR: ${validation.compliance.gdpr}/100</li>
            <li>ISO 27001: ${validation.compliance.iso27001}/100</li>
            <li>SOC 2: ${validation.compliance.soc2}/100</li>
        </ul>
    </body>
    </html>
  `;
}
```

### 6. Docker Integration Example

```dockerfile
# Dockerfile.bmad-agent
FROM node:18-alpine

WORKDIR /app

# Install BMAD CLI and dependencies
RUN npm install -g @bmad/architectural-design-cli

# Copy requirements and configuration
COPY requirements.yaml .
COPY architecture-config.yaml .

# Generate architecture
RUN bmad-arch generate \
    --requirements ./requirements.yaml \
    --config ./architecture-config.yaml \
    --output ./output/

# Validate architecture
RUN bmad-arch validate \
    --architecture ./output/ \
    --standards gdpr,iso27001

# Generate implementation guide
RUN bmad-arch roadmap \
    --architecture ./output/ \
    --format markdown \
    --output ./implementation-guide.md

VOLUME ["/app/output"]
CMD ["cat", "./implementation-guide.md"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  bmad-agent:
    build:
      context: .
      dockerfile: Dockerfile.bmad-agent
    volumes:
      - ./requirements.yaml:/app/requirements.yaml:ro
      - ./architecture-config.yaml:/app/architecture-config.yaml:ro
      - ./output:/app/output
    environment:
      - BMAD_API_KEY=${BMAD_API_KEY}
      - PROJECT_ID=law-firm-2030
```

### 7. Slack Integration Example

```javascript
// slack-bot-integration.js
const { App } = require('@slack/bolt');
const { BMadArchAgent } = require('@bmad/architectural-design');

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  signingSecret: process.env.SLACK_SIGNING_SECRET
});

// Slash command to generate architecture
app.command('/bmad-arch', async ({ command, ack, respond }) => {
  await ack();
  
  const agent = new BMadArchAgent();
  const [action, ...args] = command.text.split(' ');
  
  try {
    switch (action) {
      case 'generate':
        await respond('🏗️ Generating architecture... This may take a few minutes.');
        
        const requirements = await loadRequirementsFromSlack(args[0]);
        const architecture = await agent.generateArchitecture(requirements);
        
        await respond({
          text: '✅ Architecture generated successfully!',
          attachments: [{
            title: 'Architecture Summary',
            text: architecture.summary,
            actions: [{
              type: 'button',
              text: 'View Full Architecture',
              url: architecture.documentUrl
            }]
          }]
        });
        break;
        
      case 'validate':
        const validation = await agent.validateArchitecture(args[0]);
        
        await respond({
          text: `🔍 Validation ${validation.status === 'passed' ? '✅ PASSED' : '❌ FAILED'}`,
          attachments: [{
            title: 'Validation Results',
            fields: [
              { title: 'Issues Found', value: validation.issues.length, short: true },
              { title: 'Compliance Score', value: `${validation.compliance.overall}/100`, short: true }
            ]
          }]
        });
        break;
        
      default:
        await respond('Usage: `/bmad-arch generate <requirements-url>` or `/bmad-arch validate <architecture-url>`');
    }
  } catch (error) {
    await respond(`❌ Error: ${error.message}`);
  }
});

app.start(process.env.PORT || 3000);
```

### 8. Monitoring Integration Example

```yaml
# prometheus-config.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bmad-agent'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s
    
rule_files:
  - "bmad-rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

---
# bmad-rules.yml
groups:
  - name: bmad-architecture
    rules:
      - alert: ArchitectureValidationFailed
        expr: bmad_validation_status != 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Architecture validation failed"
          description: "Architecture validation has been failing for {{ $value }} minutes"
          
      - alert: ComplianceScoreLow
        expr: bmad_compliance_score < 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Compliance score below threshold"
          description: "Compliance score is {{ $value }}/100"
```

These examples demonstrate how the BMAD Architectural Design Agent can be integrated into various development workflows, from CLI tools and IDEs to CI/CD pipelines and team collaboration platforms, providing comprehensive architectural guidance throughout the development lifecycle.