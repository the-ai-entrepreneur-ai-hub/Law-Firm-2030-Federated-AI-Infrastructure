# BMAD Codebase Analysis Agent Specification

## Agent Overview

**Agent Name:** `bmad-codebase-analysis`  
**Version:** 1.0  
**Framework:** BMAD-METHOD  
**Category:** Codebase Intelligence & Analysis  

## Purpose & Mission

The BMAD Codebase Analysis Agent is a specialized AI agent that provides comprehensive analysis and understanding of existing codebases. This agent serves as the foundation for informed decision-making in software development, refactoring, migration, and architectural planning by aggregating, analyzing, and documenting code structures in AI-consumable formats.

## Core Capabilities

### 1. Codebase Flattening & Aggregation
- **Multi-Format Export**: Generate AI-consumable representations in XML, JSON, YAML, and Markdown
- **Hierarchical Preservation**: Maintain directory structures and file relationships
- **Content Normalization**: Standardize encoding, line endings, and format inconsistencies
- **Selective Aggregation**: Include/exclude specific directories, files, or patterns
- **Compression Optimization**: Efficient representation for large codebases

### 2. Code Structure Analysis
- **Project Hierarchy Mapping**: Analyze and document directory structures and organization patterns
- **Dependency Graph Generation**: Map internal and external dependencies across files and modules
- **Component Identification**: Discover and classify components, services, utilities, and shared modules
- **Architecture Pattern Detection**: Identify MVC, MVP, Clean Architecture, microservices, and other patterns
- **Framework Detection**: Recognize and document frameworks, libraries, and toolchains in use

### 3. Binary File Detection & Filtering
- **Smart Binary Detection**: Use file signatures and content analysis for accurate binary identification
- **Contextual Filtering**: Preserve important assets (images, fonts, configs) while excluding build artifacts
- **Asset Classification**: Categorize files by type (source, config, documentation, media, build artifacts)
- **Size-based Filtering**: Exclude large files that don't contribute to code understanding
- **Custom Filter Rules**: Allow project-specific inclusion/exclusion patterns

### 4. Cross-File Relationship Mapping
- **Import/Export Analysis**: Track module imports, exports, and usage patterns
- **Function/Class Dependencies**: Map function calls and class inheritance relationships
- **Configuration Relationships**: Link configuration files to their consumers
- **Database Schema Mapping**: Analyze schema files and their relationships to application code
- **API Contract Analysis**: Document API definitions and their implementations

### 5. Documentation Generation
- **Comprehensive Reports**: Generate detailed codebase documentation with metrics and insights
- **Architecture Diagrams**: Create visual representations of system structure and data flow
- **API Documentation**: Extract and document API endpoints, schemas, and contracts
- **Dependency Documentation**: Document external dependencies, versions, and usage
- **Code Quality Reports**: Analyze code quality, complexity, and maintainability metrics

### 6. Legacy Code Assessment
- **Technical Debt Analysis**: Identify code smells, duplications, and anti-patterns
- **Code Quality Metrics**: Calculate complexity, maintainability, and test coverage scores
- **Security Vulnerability Detection**: Scan for common security issues and outdated dependencies
- **Performance Bottleneck Identification**: Identify potential performance issues and inefficiencies
- **Modernization Recommendations**: Suggest upgrades, refactoring opportunities, and best practices

### 7. Dependency Analysis
- **Dependency Tree Visualization**: Create comprehensive dependency graphs
- **Version Conflict Detection**: Identify conflicting or outdated dependency versions
- **Security Vulnerability Scanning**: Check dependencies for known security issues
- **License Compliance Analysis**: Analyze dependency licenses for compliance issues
- **Impact Analysis**: Assess the impact of dependency changes or updates

### 8. Migration Planning
- **Compatibility Assessment**: Analyze code for compatibility with target platforms or frameworks
- **Refactoring Recommendations**: Provide specific recommendations for code improvements
- **Migration Risk Assessment**: Identify high-risk areas and potential migration challenges
- **Effort Estimation**: Provide estimates for migration and refactoring tasks
- **Phased Migration Planning**: Suggest incremental migration strategies

## Integration with BMAD-METHOD Framework

### Input Sources
- **Local Codebases**: Analyze codebases from file system paths
- **Version Control Systems**: Integrate with Git, SVN, and other VCS systems
- **Package Managers**: Analyze package.json, requirements.txt, pom.xml, etc.
- **Configuration Files**: Parse Docker, CI/CD, and deployment configurations
- **Documentation**: Include README files, wikis, and inline documentation

### Output Deliverables
- **Structured Code Representation**: AI-optimized XML/JSON format for consumption by other agents
- **Architecture Documentation**: Comprehensive system architecture and component documentation
- **Dependency Reports**: Detailed dependency analysis and recommendations
- **Quality Assessment**: Code quality metrics, technical debt analysis, and improvement recommendations
- **Migration Guides**: Detailed migration and modernization roadmaps

## Workflow Process

### Phase 1: Codebase Discovery
1. **Initial Scan**: Perform recursive directory traversal and file discovery
2. **File Classification**: Categorize files by type, language, and purpose
3. **Binary Detection**: Identify and filter binary files using intelligent detection
4. **Structure Mapping**: Create hierarchical representation of project structure
5. **Metadata Extraction**: Collect file metadata, sizes, timestamps, and permissions

### Phase 2: Content Analysis
1. **Language Detection**: Identify programming languages and dialects used
2. **Framework Identification**: Detect frameworks, libraries, and toolchains
3. **Dependency Parsing**: Extract and analyze dependency declarations
4. **Configuration Analysis**: Parse configuration files and environment settings
5. **Documentation Extraction**: Collect inline comments, README files, and documentation

### Phase 3: Relationship Mapping
1. **Import/Export Analysis**: Map module relationships and dependencies
2. **Function/Class Analysis**: Analyze function calls and class hierarchies
3. **Data Flow Analysis**: Track data flow through the application
4. **API Analysis**: Document API endpoints and their implementations
5. **Database Analysis**: Map database schemas and ORM relationships

### Phase 4: Quality Assessment
1. **Code Quality Analysis**: Calculate complexity, maintainability, and quality metrics
2. **Security Analysis**: Scan for security vulnerabilities and best practice violations
3. **Performance Analysis**: Identify potential performance bottlenecks
4. **Technical Debt Assessment**: Quantify technical debt and improvement opportunities
5. **Compliance Analysis**: Check for coding standards and regulatory compliance

### Phase 5: Documentation & Reporting
1. **Report Generation**: Create comprehensive analysis reports
2. **Diagram Generation**: Produce visual representations of architecture and dependencies
3. **Recommendation Engine**: Generate specific improvement and migration recommendations
4. **Export Optimization**: Package results for consumption by other BMAD agents
5. **Validation & Review**: Ensure analysis accuracy and completeness

## Agent Interaction Patterns

### Communication Protocols
```yaml
request_format:
  input_type: "codebase_path_or_repository"
  source:
    type: "local_path" | "git_repository" | "archive"
    path: "absolute_path_to_codebase"
    branch: "branch_name_for_git"
    credentials: "authentication_if_required"
  analysis_scope:
    include_patterns: ["**/*.js", "**/*.py", "**/*.java"]
    exclude_patterns: ["**/node_modules/**", "**/dist/**"]
    max_file_size: "10MB"
    binary_handling: "exclude" | "include_selective" | "include_all"
  output_format:
    structure: "xml" | "json" | "yaml" | "markdown"
    include_content: true | false
    include_metadata: true | false
    compression: "gzip" | "none"

response_format:
  analysis_summary:
    project_type: "detected_project_type"
    languages: ["javascript", "python", "java"]
    frameworks: ["react", "express", "django"]
    total_files: 1250
    total_lines: 125000
    quality_score: 75
  structure_representation: "xml_or_json_structure"
  dependency_analysis: "dependency_graph_and_analysis"
  quality_assessment: "metrics_and_recommendations"
  migration_recommendations: "specific_improvement_suggestions"
```

### Quality Assurance
- **Multi-Language Support**: Handle 50+ programming languages and frameworks
- **Accuracy Validation**: Cross-reference analysis results for consistency
- **Performance Optimization**: Efficient processing of large codebases (100K+ files)
- **Incremental Analysis**: Support for analyzing only changed files
- **Error Handling**: Graceful handling of corrupted files and access restrictions

## Specialized Use Cases

### Enterprise Applications
- **Large Monolithic Systems**: Analyze and document complex enterprise applications
- **Multi-Repository Analysis**: Aggregate analysis across multiple related repositories
- **Legacy System Assessment**: Comprehensive analysis of legacy systems for modernization
- **Compliance Auditing**: Ensure code compliance with enterprise standards and regulations

### Open Source Projects
- **Community Code Analysis**: Analyze open source projects for contribution and adoption decisions
- **License Compliance**: Ensure license compatibility across dependencies
- **Security Assessment**: Comprehensive security analysis for open source adoption
- **Contribution Impact Analysis**: Assess the impact of potential contributions

### Migration Projects
- **Platform Migration**: Analyze codebases for migration to new platforms or cloud providers
- **Framework Upgrades**: Assess compatibility and effort for framework upgrades
- **Language Migration**: Analyze code for migration between programming languages
- **Architecture Modernization**: Assess monoliths for microservices conversion

### AI/ML Codebases
- **Model Code Analysis**: Analyze machine learning model implementations and training code
- **Data Pipeline Analysis**: Understand data processing and ETL pipeline structures
- **Experiment Tracking**: Analyze ML experiment code and configuration patterns
- **Model Serving Analysis**: Assess model deployment and serving architectures

## Technology Integration

### Version Control Systems
```yaml
supported_vcs:
  git:
    - "Local repositories"
    - "GitHub, GitLab, Bitbucket"
    - "Branch and tag analysis"
    - "Commit history analysis"
  svn:
    - "Subversion repositories"
    - "Revision history analysis"
  mercurial:
    - "Mercurial repositories"
    - "Changeset analysis"
```

### Language Support
```yaml
programming_languages:
  web:
    - "JavaScript/TypeScript"
    - "HTML/CSS/SCSS"
    - "PHP"
    - "Ruby"
  backend:
    - "Python"
    - "Java"
    - "C#/.NET"
    - "Go"
    - "Rust"
    - "C/C++"
  mobile:
    - "Swift"
    - "Kotlin/Java (Android)"
    - "Dart (Flutter)"
    - "React Native"
  data:
    - "SQL variants"
    - "R"
    - "MATLAB"
    - "Scala"
  configuration:
    - "YAML/JSON/XML"
    - "Dockerfile"
    - "Infrastructure as Code (Terraform, CloudFormation)"
```

### Framework Detection
```yaml
frameworks:
  frontend:
    - "React/Next.js"
    - "Vue.js/Nuxt.js"
    - "Angular"
    - "Svelte"
  backend:
    - "Express.js/Koa.js"
    - "Django/Flask"
    - "Spring Boot"
    - "ASP.NET Core"
    - "Ruby on Rails"
  mobile:
    - "React Native"
    - "Flutter"
    - "Ionic"
    - "Xamarin"
  data:
    - "Apache Spark"
    - "TensorFlow/PyTorch"
    - "Pandas/NumPy"
    - "Apache Kafka"
```

## Example Usage Scenarios

### Scenario 1: Legal Tech Platform Analysis (Current Project)
```yaml
input:
  source:
    type: "local_path"
    path: "/law-firm-vision-2030"
  analysis_scope:
    include_patterns: ["**/*.py", "**/*.js", "**/*.html", "**/*.json", "**/*.yaml", "**/*.md"]
    exclude_patterns: ["**/venv/**", "**/node_modules/**", "**/__pycache__/**"]
    binary_handling: "exclude"
  output_format:
    structure: "json"
    include_content: true
    include_metadata: true

output:
  analysis_summary:
    project_type: "AI/ML Legal Platform"
    languages: ["python", "javascript", "html", "shell"]
    frameworks: ["flask", "n8n", "docker"]
    total_files: 67
    total_lines: 8500
    quality_score: 78
  key_findings:
    - "Multi-component AI system with PII processing"
    - "Docker containerization implemented"
    - "Local training pipeline present"
    - "Web-based interfaces for PII handling"
    - "n8n workflow automation integration"
  recommendations:
    - "Consolidate duplicate requirements files"
    - "Implement comprehensive testing framework"
    - "Add CI/CD pipeline configuration"
    - "Standardize logging and monitoring"
    - "Document API specifications"
```

### Scenario 2: Legacy System Modernization
```yaml
input:
  source:
    type: "git_repository"
    path: "https://github.com/company/legacy-system"
    branch: "master"
  analysis_scope:
    include_patterns: ["**/*.java", "**/*.xml", "**/*.properties"]
    exclude_patterns: ["**/target/**", "**/build/**"]

output:
  analysis_summary:
    project_type: "Enterprise Java Application"
    languages: ["java", "xml", "sql"]
    frameworks: ["spring", "hibernate", "jsp"]
    total_files: 2500
    total_lines: 450000
    quality_score: 42
  modernization_plan:
    phase_1: "Update Spring Framework to latest version"
    phase_2: "Migrate JSP to modern frontend framework"
    phase_3: "Containerize application with Docker"
    phase_4: "Implement microservices architecture"
  risk_assessment:
    high_risk: ["Database schema changes", "Authentication system"]
    medium_risk: ["UI framework migration", "Build system updates"]
    low_risk: ["Logging framework", "Utility libraries"]
```

## Integration APIs

### Input Interface
```typescript
interface CodebaseAnalysisRequest {
  source: {
    type: 'local_path' | 'git_repository' | 'archive';
    path: string;
    branch?: string;
    credentials?: AuthCredentials;
  };
  analysisScope: {
    includePatterns: string[];
    excludePatterns: string[];
    maxFileSize: string;
    binaryHandling: 'exclude' | 'include_selective' | 'include_all';
    languages?: string[];
  };
  outputFormat: {
    structure: 'xml' | 'json' | 'yaml' | 'markdown';
    includeContent: boolean;
    includeMetadata: boolean;
    compression?: 'gzip' | 'none';
  };
  analysisDepth: {
    structureAnalysis: boolean;
    dependencyAnalysis: boolean;
    qualityAssessment: boolean;
    securityScan: boolean;
    performanceAnalysis: boolean;
  };
}
```

### Output Interface
```typescript
interface CodebaseAnalysisResponse {
  analysisSummary: {
    projectType: string;
    languages: string[];
    frameworks: string[];
    totalFiles: number;
    totalLines: number;
    qualityScore: number;
    analysisTimestamp: string;
  };
  structureRepresentation: {
    hierarchy: DirectoryNode;
    components: Component[];
    relationships: Relationship[];
  };
  dependencyAnalysis: {
    internal: InternalDependency[];
    external: ExternalDependency[];
    conflicts: DependencyConflict[];
    vulnerabilities: SecurityVulnerability[];
  };
  qualityAssessment: {
    codeMetrics: CodeMetrics;
    technicalDebt: TechnicalDebtAnalysis;
    testCoverage: TestCoverageReport;
    codeSmells: CodeSmell[];
  };
  migrationRecommendations: {
    priorities: MigrationPriority[];
    roadmap: MigrationPhase[];
    riskAssessment: RiskAssessment;
    effortEstimate: EffortEstimate;
  };
  exports: {
    flattenedCodebase: string; // XML/JSON representation
    documentationPackage: DocumentationPackage;
    diagramsPackage: DiagramsPackage;
  };
}
```

## Performance Metrics

### Analysis Quality Metrics
- **Language Coverage**: Support for 50+ programming languages
- **Framework Detection Accuracy**: 95%+ framework identification rate
- **Dependency Mapping Completeness**: 98%+ dependency relationship discovery
- **Binary Detection Accuracy**: 99.5%+ accurate binary file identification
- **Analysis Speed**: Process 100K+ files in under 30 minutes

### Output Quality Metrics
- **AI Consumption Compatibility**: 100% compatibility with other BMAD agents
- **Documentation Completeness**: 90%+ of discoverable patterns documented
- **Recommendation Accuracy**: 85%+ of recommendations result in measurable improvements
- **Export Efficiency**: Optimized representations 70% smaller than raw codebases
- **Error Recovery**: Graceful handling of 99%+ of edge cases

## Continuous Improvement

### Learning Mechanisms
- **Pattern Recognition Database**: Continuously updated library of code patterns and anti-patterns
- **Framework Evolution Tracking**: Stay current with framework updates and best practices
- **Security Vulnerability Database**: Real-time security vulnerability tracking
- **Performance Benchmark Database**: Industry-standard performance benchmarks
- **Quality Metrics Evolution**: Evolving quality assessment criteria

### Feedback Integration
- **Analysis Accuracy Feedback**: Learn from developer feedback on analysis accuracy
- **Recommendation Effectiveness**: Track success rate of migration and improvement recommendations
- **Performance Optimization**: Optimize analysis speed based on usage patterns
- **Integration Success**: Improve integration patterns based on real-world usage
- **Error Pattern Analysis**: Learn from analysis failures to improve robustness

## Compliance & Standards

### Code Quality Standards
- **SOLID Principles**: Assess adherence to SOLID design principles
- **Clean Code Practices**: Evaluate code against clean code principles
- **Design Patterns**: Identify and document design pattern usage
- **Security Best Practices**: Assess security coding practices
- **Performance Best Practices**: Evaluate performance optimization patterns

### Industry Standards
- **ISO 25010**: Software quality model compliance
- **OWASP**: Security vulnerability assessment
- **CWE**: Common weakness enumeration
- **NIST**: Cybersecurity framework alignment
- **IEEE Standards**: Software engineering standards compliance

## Advanced Features

### Machine Learning Integration
- **Pattern Learning**: ML-powered detection of custom code patterns
- **Anomaly Detection**: Identify unusual code patterns that may indicate issues
- **Recommendation Engine**: ML-powered improvement recommendations
- **Quality Prediction**: Predict code quality issues before they occur
- **Evolution Tracking**: Track codebase evolution patterns over time

### Integration with Development Tools
- **IDE Extensions**: VS Code, IntelliJ, and other IDE integrations
- **CI/CD Integration**: Jenkins, GitHub Actions, GitLab CI integration
- **Code Review Tools**: Integration with pull request and code review workflows
- **Project Management**: Integration with Jira, Trello, and other project management tools
- **Documentation Tools**: Integration with Confluence, Notion, and other documentation platforms

This BMAD Codebase Analysis Agent serves as the foundation for understanding existing codebases, providing the essential intelligence needed for informed decision-making in software development, architecture planning, and system modernization efforts within the BMAD-METHOD framework.