# BMAD Claude Agents - Implementation Guide

## Quick Start

### 1. Load the BMad Orchestrator
Copy and paste the contents of `agents/bmad-orchestrator.md` into Claude, then follow the activation instructions.

### 2. Use Commands
All agent commands start with `*`:
- `*help` - Show available capabilities
- `*agent [name]` - Switch to a specialized agent
- `*workflow` - Start a development workflow
- `*status` - Check current progress

### 3. Example Usage Flow
```
User: *help
Claude: [Shows BMad Orchestrator help with all available agents and workflows]

User: *agent analyst
Claude: [Transforms into Mary, the Business Analyst]

User: *research
Claude: [Conducts market research using analyst capabilities]

User: *exit
Claude: [Returns to BMad Orchestrator]

User: *agent pm
Claude: [Transforms into Sarah, the Product Manager]
```

## Agent Overview

### Core Agents

| Agent | Name | Role | Key Capabilities |
|-------|------|------|------------------|
| `*agent orchestrator` | BMad Orchestrator | Master Coordinator | Agent switching, workflow guidance |
| `*agent analyst` | Mary | Business Analyst | Market research, competitive analysis, brainstorming |
| `*agent pm` | Sarah | Product Manager | PRD creation, user stories, product roadmaps |
| `*agent architect` | Alex | Tech Architect | System design, architecture documentation |
| `*agent dev` | James | Developer | Code implementation, debugging, testing |
| `*agent sm` | Mike | Scrum Master | Story creation, sprint planning, workflow management |
| `*agent qa` | Lisa | QA Engineer | Test planning, quality assurance, automation |
| `*agent ux` | Emma | UX Expert | User research, wireframing, usability testing |

### Agent Commands

Each specialized agent has unique commands:

#### Business Analyst (Mary)
- `*research` - Conduct market research
- `*compete` - Competitive analysis
- `*brainstorm` - Structured ideation sessions
- `*brief` - Create project briefs
- `*elicit` - Advanced requirements gathering

#### Product Manager (Sarah)
- `*prd` - Create Product Requirements Document
- `*story` - Create user stories
- `*roadmap` - Develop product roadmap
- `*prioritize` - Feature prioritization
- `*metrics` - Define success metrics

#### Technical Architect (Alex)
- `*design` - System architecture design
- `*review` - Architecture reviews
- `*tech` - Technology selection
- `*security` - Security architecture
- `*performance` - Performance optimization

#### Developer (James)
- `*implement` - Build features
- `*debug` - Fix issues
- `*refactor` - Improve code quality
- `*test` - Create tests
- `*review` - Code reviews

#### Scrum Master (Mike)
- `*story` - Create development stories
- `*sprint` - Sprint planning
- `*standup` - Daily standup facilitation
- `*retro` - Retrospectives
- `*workflow` - Process optimization

#### QA Engineer (Lisa)
- `*plan` - Test planning
- `*test` - Test execution
- `*automate` - Test automation
- `*report` - Quality reporting
- `*acceptance` - User acceptance testing

#### UX Expert (Emma)
- `*research` - User research
- `*persona` - Create personas
- `*wireframe` - Create wireframes
- `*prototype` - Build prototypes
- `*usability` - Usability testing

## Workflow Integration

### Available Workflows
1. **Greenfield Development** - New application development
2. **Brownfield Enhancement** - Enhancing existing systems
3. **Architecture Review** - Technical assessment
4. **Product Discovery** - New product planning

### Workflow Commands
- `*workflow` - List available workflows
- `*workflow [name]` - Start specific workflow
- `*workflow-guidance` - Get personalized workflow help
- `*plan` - Create detailed project plan

## Implementation Best Practices

### 1. Start with the Orchestrator
Always begin by loading the BMad Orchestrator agent to:
- Understand available capabilities
- Get workflow recommendations
- Switch between agents efficiently

### 2. Follow the Natural Flow
For new projects, follow this sequence:
1. Business Analyst → Market research and requirements
2. Product Manager → PRD and user stories
3. Technical Architect → System design
4. UX Expert → User experience design
5. Scrum Master → Development stories
6. Developer → Implementation
7. QA Engineer → Testing and validation

### 3. Use Agent Switching
- Use `*exit` to return to the Orchestrator
- Switch agents based on current needs
- Each agent maintains context of their deliverables

### 4. Leverage Agent Specialization
Each agent is optimized for specific tasks:
- Don't ask the Developer to do market research
- Don't ask the Business Analyst to write code
- Use the right agent for the right job

## Security and Defensive Practices

### Built-in Security Features
- All agents focus on defensive security tasks only
- Input validation and sanitization guidance
- Secure coding practice recommendations
- Security architecture considerations
- Accessibility and compliance requirements

### Limitations
- Agents will refuse to create malicious code
- No assistance with offensive security tasks
- Focus on legitimate defensive security needs
- Audit trail of decisions and actions

## Customization and Extension

### Adapting Agents
Each agent can be customized by:
1. Modifying the persona and core principles
2. Adding domain-specific commands
3. Including additional expertise areas
4. Updating help documentation

### Creating New Agents
Use the existing agent structure:
1. Define agent metadata (name, role, icon)
2. Create persona and core principles
3. Define available commands and capabilities
4. Add behavioral guidelines
5. Include help documentation and templates

## Troubleshooting

### Common Issues
1. **Agent not responding correctly**: Ensure activation instructions were followed completely
2. **Commands not working**: Verify commands start with `*`
3. **Context loss**: Use `*status` to check current state
4. **Workflow confusion**: Return to orchestrator with `*exit`

### Getting Help
- Use `*help` in any agent for available commands
- Use `*status` to understand current context
- Return to orchestrator for workflow guidance
- Check agent documentation for specific capabilities

## Example Project Flow

### Building a New Web Application

```
1. Load BMad Orchestrator
   → *help (understand capabilities)
   → *workflow greenfield-fullstack

2. Business Analysis Phase
   → *agent analyst
   → *research (market analysis)
   → *compete (competitive analysis)
   → *brief (project brief)

3. Product Definition Phase
   → *exit (return to orchestrator)
   → *agent pm
   → *prd (requirements document)
   → *story (user stories)
   → *roadmap (product timeline)

4. Architecture Phase
   → *exit
   → *agent architect
   → *design (system architecture)
   → *tech (technology selection)
   → *security (security design)

5. UX Design Phase
   → *exit
   → *agent ux
   → *research (user research)
   → *wireframe (layouts)
   → *prototype (interactive prototype)

6. Development Phase
   → *exit
   → *agent sm
   → *story (development stories)
   → *sprint (sprint planning)

7. Implementation Phase
   → *exit
   → *agent dev
   → *implement (build features)
   → *test (create tests)

8. Quality Assurance
   → *exit
   → *agent qa
   → *plan (test planning)
   → *test (execute tests)
   → *automate (test automation)
```

## Success Metrics

### Planning Phase Success
- [ ] Market opportunity validated
- [ ] Requirements clearly defined
- [ ] Architecture approved
- [ ] User experience tested

### Development Phase Success
- [ ] All stories implemented
- [ ] Code quality standards met
- [ ] Comprehensive testing completed
- [ ] Security requirements satisfied

### Deployment Success
- [ ] Production deployment successful
- [ ] Performance meets requirements
- [ ] User acceptance criteria met
- [ ] Monitoring and support operational

---

**The BMAD Claude Agents provide a comprehensive framework for managing software development projects through specialized AI agents. Start with the Orchestrator and let it guide you through the appropriate workflow for your needs.**