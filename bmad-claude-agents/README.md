# BMAD Method Claude Agents

This repository contains Claude-compatible implementations of the BMAD (Breakthrough Method of Agile AI-Driven Development) agents, adapted from the original BMAD-METHOD framework.

## Overview

The BMAD method transforms traditional software development through specialized AI agents that collaborate in an agile workflow. This implementation makes these agents compatible with Claude and other LLMs.

## Core Agents

### 1. BMad Orchestrator
- **Role**: Master coordinator and agent switcher
- **Use**: Workflow coordination, multi-agent tasks, role switching
- **Key Features**: Can transform into any specialized agent dynamically

### 2. Business Analyst (Mary)
- **Role**: Strategic analysis and ideation partner  
- **Use**: Market research, brainstorming, competitive analysis, project briefs
- **Key Features**: Advanced elicitation methods, structured analysis

### 3. Developer (James)
- **Role**: Full-stack implementation specialist
- **Use**: Code implementation, debugging, refactoring
- **Key Features**: Story-driven development, comprehensive testing

### 4. Product Manager (PM)
- **Role**: Product strategy and requirements
- **Use**: PRD creation, feature prioritization, stakeholder alignment
- **Key Features**: User story management, product roadmapping

### 5. Architect
- **Role**: Technical architecture and system design
- **Use**: System design, technical documentation, architecture reviews
- **Key Features**: Scalable architecture patterns, technology selection

### 6. Scrum Master (SM)
- **Role**: Workflow orchestration and story management
- **Use**: Sprint planning, story creation, workflow optimization
- **Key Features**: Agile process enforcement, team coordination

### 7. QA Engineer
- **Role**: Quality assurance and testing
- **Use**: Test planning, quality validation, bug tracking
- **Key Features**: Automated testing strategies, quality metrics

### 8. UX Expert
- **Role**: User experience design
- **Use**: Interface design, user research, usability testing
- **Key Features**: Design systems, user journey mapping

## Usage with Claude

Each agent can be activated by:
1. Loading the agent's markdown file
2. Following the activation instructions
3. Using the command system (all commands start with `*`)

## Agent Command System

All agents support these core commands:
- `*help` - Show available commands and capabilities
- `*status` - Show current context and progress  
- `*task [name]` - Execute specific tasks
- `*checklist [name]` - Run quality checklists
- `*exit` - Return to orchestrator or exit

## Workflow Integration

The agents follow the BMAD two-phase approach:
1. **Planning Phase**: Analyst, PM, and Architect create comprehensive specifications
2. **Development Phase**: SM, Developer, and QA execute through detailed stories

## Files Structure

```
bmad-claude-agents/
├── agents/
│   ├── bmad-orchestrator.md
│   ├── business-analyst.md
│   ├── developer.md
│   ├── product-manager.md
│   ├── architect.md
│   ├── scrum-master.md
│   ├── qa-engineer.md
│   └── ux-expert.md
├── tasks/
├── templates/
├── checklists/
└── workflows/
```

## Getting Started

1. Choose an agent based on your current need
2. Load the agent file with Claude
3. Follow the activation instructions in the file
4. Use `*help` to see available commands
5. Execute tasks or switch agents as needed

## Key Differences from Original BMAD

- Optimized for Claude's capabilities and limitations
- Simplified file structure for easier loading
- Enhanced command system for better usability
- Integrated defensive security practices
- Added comprehensive documentation

## License

MIT License - Compatible with original BMAD-METHOD licensing