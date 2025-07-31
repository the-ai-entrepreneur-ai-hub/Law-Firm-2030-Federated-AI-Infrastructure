---
description: "Show BMAD system help and usage instructions"
---

# BMAD System Help

The BMAD (Breakthrough Method of Agile AI-Driven Development) agent system provides specialized AI agents for software development.

## Core Commands:

- `/agents` - Show available agents and how to load them
- `/load-agent <name>` - Load and activate a specific agent
- `/bmad-help` - Show this help information

## Agent System:

### 🎭 Master Coordinator
- **orchestrator** - BMad Orchestrator for workflow guidance and agent switching

### 👥 Planning Team
- **analyst** - Mary (Market research, competitive analysis, brainstorming)
- **pm** - Sarah (PRD creation, user stories, product roadmaps)
- **architect** - Alex (System design, architecture, technology selection)
- **ux** - Emma (User research, wireframing, usability testing)

### 🛠️ Development Team  
- **dev** - James (Full-stack implementation, debugging, testing)
- **sm** - Mike (Story creation, sprint planning, workflow management)
- **qa** - Lisa (Test planning, automation, quality assurance)

## Workflow:

1. **Start**: `/load-agent orchestrator` for guided workflows
2. **Plan**: Use analyst → pm → architect → ux for requirements and design
3. **Build**: Use sm → dev → qa for implementation and testing
4. **Switch**: Each agent can recommend next steps and agent transitions

## Agent Commands:

Once an agent is loaded, use commands starting with `*`:
- `*help` - Show agent-specific capabilities
- `*status` - Show current context and progress  
- `*exit` - Return to agent selection
- `*[agent-specific]` - Each agent has unique commands

## Example Usage:

```
/load-agent orchestrator
*help
*workflow greenfield-fullstack
*agent analyst
*research
*exit
/load-agent pm
*prd
```

## Documentation:

Full documentation and implementation guides are available in:
- `bmad-claude-agents/README.md`
- `bmad-claude-agents/IMPLEMENTATION-GUIDE.md`
- `bmad-claude-agents/workflows/`

💡 **Quick Start**: Type `/load-agent orchestrator` to begin with guided workflow selection!