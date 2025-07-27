# BMAD Codebase Analysis CLI Tool Specification

## Overview

The BMAD Codebase Analysis CLI tool provides a command-line interface for comprehensive codebase analysis, flattening, and AI-consumable output generation. This tool is designed to integrate seamlessly with the BMAD-METHOD framework and provide developers with powerful codebase intelligence capabilities.

## Installation

```bash
# Install via npm (Node.js)
npm install -g @bmad/codebase-analysis-cli

# Install via pip (Python)
pip install bmad-codebase-analysis

# Install via binary download
curl -L https://github.com/bmad/codebase-analysis/releases/latest/download/bmad-codebase-linux-amd64 -o bmad-codebase
chmod +x bmad-codebase
sudo mv bmad-codebase /usr/local/bin/
```

## Command Structure

```bash
bmad-codebase <command> [options] [arguments]
```

## Core Commands

### 1. Initialize Project Analysis

```bash
# Initialize BMAD analysis for a project
bmad-codebase init [path] [options]

# Examples
bmad-codebase init .
bmad-codebase init /path/to/project --config custom-config.yaml
bmad-codebase init https://github.com/user/repo.git --branch main
```

**Options:**
- `--config, -c`: Specify configuration file
- `--project-type`: Override auto-detected project type
- `--output, -o`: Output directory for analysis results
- `--branch, -b`: Git branch to analyze (for repositories)

### 2. Comprehensive Analysis

```bash
# Perform comprehensive codebase analysis
bmad-codebase analyze [path] [options]

# Examples
bmad-codebase analyze . --output ./analysis
bmad-codebase analyze /path/to/law-firm-2030 --include "**/*.py,**/*.js" --exclude "**/venv/**"
bmad-codebase analyze . --security-focus --compliance gdpr,hipaa
```

**Options:**
- `--include`: File patterns to include (glob patterns)
- `--exclude`: File patterns to exclude (glob patterns)
- `--output, -o`: Output directory
- `--format`: Output format (json, yaml, xml, markdown)
- `--security-focus`: Enable enhanced security analysis
- `--compliance`: Compliance standards to check (gdpr, hipaa, sox, etc.)
- `--quality-threshold`: Minimum quality score threshold
- `--parallel, -p`: Number of parallel analysis threads

### 3. Codebase Flattening

```bash
# Generate flattened representation for AI consumption
bmad-codebase flatten [path] [options]

# Examples
bmad-codebase flatten . --format json --output flattened.json
bmad-codebase flatten /project --ai-optimized --compress gzip
bmad-codebase flatten . --include-content --max-file-size 1MB
```

**Options:**
- `--format`: Output format (json, xml, yaml)
- `--include-content`: Include file contents in output
- `--include-metadata`: Include file metadata
- `--max-file-size`: Maximum file size to include
- `--ai-optimized`: Optimize for AI model consumption
- `--compress`: Compression format (gzip, bzip2, none)

### 4. Dependency Analysis

```bash
# Analyze project dependencies
bmad-codebase dependencies [path] [options]

# Examples
bmad-codebase dependencies . --check-vulnerabilities
bmad-codebase dependencies /project --output deps.json --include-dev
bmad-codebase dependencies . --license-check --format csv
```

**Options:**
- `--check-vulnerabilities`: Check for security vulnerabilities
- `--include-dev`: Include development dependencies
- `--license-check`: Analyze dependency licenses
- `--format`: Output format (json, csv, yaml)
- `--severity-threshold`: Minimum vulnerability severity to report

### 5. Security Audit

```bash
# Perform security-focused analysis
bmad-codebase audit [path] [options]

# Examples
bmad-codebase audit . --output security-report.json
bmad-codebase audit /project --include-secrets --check-compliance gdpr
bmad-codebase audit . --severity high --export-sarif
```

**Options:**
- `--include-secrets`: Scan for hardcoded secrets
- `--check-compliance`: Compliance frameworks to check
- `--severity`: Minimum severity level (low, medium, high, critical)
- `--export-sarif`: Export results in SARIF format
- `--custom-rules`: Path to custom security rules file

### 6. Quality Assessment

```bash
# Assess code quality metrics
bmad-codebase quality [path] [options]

# Examples
bmad-codebase quality . --output quality-report.html
bmad-codebase quality /project --threshold 80 --fail-on-threshold
bmad-codebase quality . --include-complexity --include-duplication
```

**Options:**
- `--threshold`: Quality score threshold
- `--fail-on-threshold`: Exit with error if threshold not met
- `--include-complexity`: Include complexity analysis
- `--include-duplication`: Include code duplication analysis
- `--format`: Report format (html, json, yaml, pdf)

### 7. Migration Planning

```bash
# Generate migration recommendations
bmad-codebase migrate [path] [options]

# Examples
bmad-codebase migrate . --target microservices --timeline 6months
bmad-codebase migrate /legacy --framework react --output migration-plan.md
bmad-codebase migrate . --cloud aws --compliance gdpr
```

**Options:**
- `--target`: Target architecture (microservices, serverless, cloud-native)
- `--framework`: Target framework
- `--cloud`: Target cloud provider (aws, azure, gcp)
- `--timeline`: Project timeline
- `--budget`: Budget constraints
- `--compliance`: Compliance requirements

### 8. Documentation Generation

```bash
# Generate comprehensive documentation
bmad-codebase docs [path] [options]

# Examples
bmad-codebase docs . --output ./documentation
bmad-codebase docs /project --include-diagrams --format markdown
bmad-codebase docs . --api-docs --architecture-docs
```

**Options:**
- `--include-diagrams`: Generate architecture diagrams
- `--api-docs`: Generate API documentation
- `--architecture-docs`: Generate architecture documentation
- `--format`: Documentation format (markdown, html, pdf)
- `--template`: Documentation template to use

### 9. Comparison Analysis

```bash
# Compare codebases or versions
bmad-codebase compare [path1] [path2] [options]

# Examples
bmad-codebase compare ./v1 ./v2 --output diff-report.json
bmad-codebase compare . origin/main --git-mode
bmad-codebase compare /project1 /project2 --focus architecture
```

**Options:**
- `--git-mode`: Compare git references instead of directories
- `--focus`: Focus area (architecture, security, quality, dependencies)
- `--output`: Output file for comparison report
- `--format`: Report format (json, html, markdown)

### 10. Integration Commands

```bash
# Integration with other BMAD agents
bmad-codebase export [path] [options]

# Examples
bmad-codebase export . --target bmad-planning --output requirements.yaml
bmad-codebase export /project --target bmad-architecture --include-patterns
bmad-codebase export . --target ai-consumption --optimize
```

**Options:**
- `--target`: Target BMAD agent (bmad-planning, bmad-architecture, ai-consumption)
- `--include-patterns`: Include architectural patterns
- `--optimize`: Optimize for target agent consumption

## Configuration

### Configuration File Format

```yaml
# bmad-analysis-config.yaml
analysis:
  project:
    name: "Law Firm Vision 2030"
    type: "ai-legal-platform"
    
  scope:
    include_patterns:
      - "**/*.py"
      - "**/*.js"
      - "**/*.html"
      - "**/*.json"
    exclude_patterns:
      - "**/venv/**"
      - "**/node_modules/**"
      - "**/__pycache__/**"
    max_file_size: "10MB"
    
  analysis_depth:
    structure_analysis: true
    dependency_analysis: true
    quality_assessment: true
    security_scan: true
    
  output:
    format: "json"
    include_content: true
    compression: "gzip"
    
  quality:
    minimum_score: 70
    complexity_threshold: 15
    
  security:
    check_vulnerabilities: true
    compliance_standards: ["gdpr", "hipaa"]
    
  performance:
    parallel_threads: 4
    memory_limit: "2GB"
```

### Environment Variables

```bash
# API Configuration
export BMAD_API_KEY="your-api-key"
export BMAD_API_URL="https://api.bmad.ai"

# Performance Configuration
export BMAD_PARALLEL_THREADS=4
export BMAD_MEMORY_LIMIT="2GB"
export BMAD_CACHE_DIR="~/.bmad/cache"

# Output Configuration
export BMAD_DEFAULT_OUTPUT_FORMAT="json"
export BMAD_DEFAULT_OUTPUT_DIR="./bmad-analysis"
```

## Practical Examples

### Example 1: Legal Platform Analysis

```bash
# Complete analysis of Law Firm Vision 2030 project
bmad-codebase analyze "/path/to/Law Firm Vision 2030" \
  --include "**/*.py,**/*.js,**/*.html,**/*.json,**/*.yaml" \
  --exclude "**/venv/**,**/node_modules/**,**/__pycache__/**" \
  --security-focus \
  --compliance gdpr \
  --output ./analysis \
  --format json

# Generate flattened representation for AI consumption
bmad-codebase flatten "/path/to/Law Firm Vision 2030" \
  --ai-optimized \
  --include-content \
  --compress gzip \
  --output law-firm-flattened.json.gz

# Security audit
bmad-codebase audit "/path/to/Law Firm Vision 2030" \
  --include-secrets \
  --check-compliance gdpr,attorney-client-privilege \
  --output security-audit.json
```

### Example 2: Migration Planning

```bash
# Assess migration to microservices
bmad-codebase migrate "/path/to/monolith" \
  --target microservices \
  --cloud aws \
  --timeline "12 months" \
  --budget 2000000 \
  --output migration-plan.md

# Compare current vs target architecture
bmad-codebase compare "/path/to/current" "/path/to/target" \
  --focus architecture \
  --output architecture-diff.html
```

### Example 3: CI/CD Integration

```bash
# Quality gate check
bmad-codebase quality . \
  --threshold 80 \
  --fail-on-threshold \
  --output quality-report.json

# Dependency vulnerability check
bmad-codebase dependencies . \
  --check-vulnerabilities \
  --severity medium \
  --format json \
  --output deps-security.json

# Generate documentation
bmad-codebase docs . \
  --include-diagrams \
  --api-docs \
  --output ./docs \
  --format html
```

### Example 4: Team Collaboration

```bash
# Weekly analysis report
bmad-codebase analyze . \
  --output ./reports/week-$(date +%Y-%m-%d) \
  --format html \
  --include-complexity \
  --include-duplication

# Export for architecture review
bmad-codebase export . \
  --target bmad-architecture \
  --include-patterns \
  --output architecture-review.yaml
```

## Output Formats

### JSON Output Example

```json
{
  "analysis_metadata": {
    "timestamp": "2024-01-15T10:00:00Z",
    "version": "1.0.0",
    "analyzer": "bmad-codebase-analysis",
    "project_path": "/path/to/project"
  },
  "project_summary": {
    "name": "Law Firm Vision 2030",
    "type": "ai-legal-platform",
    "languages": ["python", "javascript"],
    "frameworks": ["flask", "docker"],
    "total_files": 67,
    "total_lines": 8500,
    "quality_score": 78
  },
  "components": [...],
  "dependencies": [...],
  "security_assessment": {...},
  "quality_metrics": {...},
  "recommendations": [...]
}
```

### YAML Output Example

```yaml
analysis_metadata:
  timestamp: "2024-01-15T10:00:00Z"
  version: "1.0.0"
  analyzer: "bmad-codebase-analysis"

project_summary:
  name: "Law Firm Vision 2030"
  type: "ai-legal-platform"
  quality_score: 78

components:
  - name: "pii_processor"
    type: "ai_ml_service"
    files: ["pii_web_app.py"]
    dependencies: ["flask", "transformers"]
```

## Error Handling

The CLI tool provides comprehensive error handling with clear error messages and exit codes:

- **Exit Code 0**: Success
- **Exit Code 1**: General error
- **Exit Code 2**: Invalid arguments
- **Exit Code 3**: File/directory not found
- **Exit Code 4**: Permission denied
- **Exit Code 5**: Quality threshold not met
- **Exit Code 6**: Security issues found
- **Exit Code 7**: Configuration error

## Integration with Development Workflows

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: bmad-quality-check
        name: BMAD Quality Check
        entry: bmad-codebase quality
        args: ['.', '--threshold', '70', '--fail-on-threshold']
        language: system
        pass_filenames: false
```

### GitHub Actions

```yaml
# .github/workflows/bmad-analysis.yml
- name: BMAD Codebase Analysis
  run: |
    bmad-codebase analyze . --output ./analysis
    bmad-codebase quality . --threshold 80 --fail-on-threshold
    bmad-codebase audit . --severity medium
```

This CLI tool specification provides a comprehensive command-line interface for the BMAD Codebase Analysis Agent, enabling developers to integrate powerful codebase analysis capabilities into their development workflows.