# Greenfield Development Workflow

This workflow guides you through creating a new software application from scratch using the BMAD Claude agents.

## Overview

The Greenfield Development workflow follows a two-phase approach:
1. **Planning Phase**: Define requirements, architecture, and design
2. **Development Phase**: Implement, test, and deploy the solution

## Phase 1: Planning

### Step 1: Business Analysis and Discovery
**Agent**: Business Analyst (Mary)
**Duration**: 1-2 weeks
**Deliverables**:
- Market research and competitive analysis
- Project brief and requirements document
- User personas and use cases
- Business objectives and success criteria

**Process**:
1. Load Business Analyst agent: `*agent analyst`
2. Conduct market research: `*research`
3. Create project brief: `*brief`
4. Facilitate requirements brainstorming: `*brainstorm`

### Step 2: Product Requirements Definition
**Agent**: Product Manager (Sarah)
**Duration**: 1-2 weeks
**Deliverables**:
- Product Requirements Document (PRD)
- User stories with acceptance criteria
- Feature prioritization and roadmap
- Success metrics and KPIs

**Process**:
1. Load Product Manager agent: `*agent pm`
2. Create comprehensive PRD: `*prd`
3. Develop user stories: `*story`
4. Create product roadmap: `*roadmap`

### Step 3: Technical Architecture Design
**Agent**: Technical Architect (Alex)
**Duration**: 1-2 weeks
**Deliverables**:
- System architecture document
- Technology stack selection
- Database and API design
- Security and scalability considerations

**Process**:
1. Load Technical Architect agent: `*agent architect`
2. Design system architecture: `*design`
3. Select technology stack: `*tech`
4. Define security architecture: `*security`

### Step 4: User Experience Design
**Agent**: UX Expert (Emma)
**Duration**: 2-3 weeks
**Deliverables**:
- User research and persona validation
- Wireframes and user flows
- Interactive prototypes
- Design system and UI specifications

**Process**:
1. Load UX Expert agent: `*agent ux`
2. Conduct user research: `*research`
3. Create wireframes: `*wireframe`
4. Build interactive prototypes: `*prototype`
5. Conduct usability testing: `*usability`

## Phase 2: Development

### Step 5: Sprint Planning and Story Creation
**Agent**: Scrum Master (Mike)
**Duration**: Ongoing (weekly sprints)
**Deliverables**:
- Detailed development stories
- Sprint plans and timelines
- Definition of Done criteria
- Team velocity metrics

**Process**:
1. Load Scrum Master agent: `*agent sm`
2. Create development stories: `*story`
3. Plan sprint activities: `*sprint`
4. Facilitate daily standups: `*standup`

### Step 6: Development and Implementation
**Agent**: Developer (James)
**Duration**: 8-12 weeks (depending on scope)
**Deliverables**:
- Working software increment
- Unit and integration tests
- Technical documentation
- Code reviews and quality assurance

**Process**:
1. Load Developer agent: `*agent dev`
2. Implement features: `*implement`
3. Debug and fix issues: `*debug`
4. Refactor for quality: `*refactor`
5. Create comprehensive tests: `*test`

### Step 7: Quality Assurance and Testing
**Agent**: QA Engineer (Lisa)
**Duration**: 2-4 weeks (parallel with development)
**Deliverables**:
- Test plans and test cases
- Automated test suites
- Quality reports and metrics
- User acceptance test results

**Process**:
1. Load QA Engineer agent: `*agent qa`
2. Create test plans: `*plan`
3. Execute comprehensive testing: `*test`
4. Implement test automation: `*automate`
5. Conduct user acceptance testing: `*acceptance`

### Step 8: Deployment and Launch
**Agent**: Developer (James) + Architect (Alex)
**Duration**: 1-2 weeks
**Deliverables**:
- Production deployment
- Monitoring and alerting setup
- Performance optimization
- Go-live checklist completion

**Process**:
1. Prepare deployment environment: `*deploy`
2. Configure monitoring and logging
3. Conduct performance testing
4. Execute go-live procedures

## Workflow Coordination

### BMad Orchestrator Commands
- `*status` - Check overall project status
- `*plan` - Create or update project plan
- `*agent [name]` - Switch to specific agent
- `*workflow-guidance` - Get workflow recommendations

### Communication and Handoffs
Each agent creates deliverables that inform the next phase:
- Analyst → Product Manager: Requirements and market insights
- Product Manager → Architect: PRD and user stories
- Architect → UX Expert: Technical constraints and capabilities
- UX Expert → Scrum Master: Design specifications and user flows
- Scrum Master → Developer: Detailed implementation stories
- Developer → QA Engineer: Code and features for testing

### Quality Gates
Before proceeding to the next phase, ensure:
1. **Planning Phase**: All stakeholders approve PRD, architecture, and designs
2. **Development Phase**: Code meets quality standards and passes all tests
3. **Launch Phase**: System meets performance and security requirements

## Success Metrics

### Planning Phase Success Criteria
- [ ] Market opportunity validated with research
- [ ] PRD approved by all stakeholders
- [ ] Architecture reviewed and approved
- [ ] User testing validates design approach

### Development Phase Success Criteria
- [ ] All user stories completed and accepted
- [ ] Code coverage meets minimum threshold (>80%)
- [ ] Performance meets defined requirements
- [ ] Security review completed with no critical issues

### Launch Success Criteria
- [ ] System deployed to production successfully
- [ ] Monitoring and alerting operational
- [ ] User acceptance testing completed
- [ ] Go-live criteria met and documented

## Timeline Template

### 16-Week Greenfield Project
```
Weeks 1-2:   Business Analysis and Discovery
Weeks 3-4:   Product Requirements Definition
Weeks 5-6:   Technical Architecture Design
Weeks 7-9:   User Experience Design
Weeks 10-15: Development and Implementation (6 sprints)
Week 16:     Deployment and Launch
```

### Parallel Activities
- QA activities run parallel with development (weeks 10-15)
- Architecture reviews occur throughout development
- Design refinements based on implementation feedback

---

**This workflow provides a structured approach to greenfield development using BMAD Claude agents. Adapt the timeline and activities based on your specific project needs and constraints.**