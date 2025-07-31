# Claude Commands - BMAD Agent System

This directory contains Claude Code slash commands that make BMAD agents directly accessible to Claude.

## Available Commands

### Core Commands
- `/agents` - Show all available BMAD agents
- `/load-agent <name>` - Load any agent by name
- `/bmad-help` - Complete system help and usage guide

### Direct Agent Loading (bmad namespace)
- `/bmad/orchestrator` - Load BMad Orchestrator (Master Coordinator)
- `/bmad/analyst` - Load Mary (Business Analyst)
- `/bmad/pm` - Load Sarah (Product Manager)  
- `/bmad/architect` - Load Alex (Technical Architect)
- `/bmad/dev` - Load James (Developer)

*Additional agents (sm, qa, ux) can be loaded via `/load-agent <name>`*

## Usage in Claude

1. **Type any slash command** in Claude Code
2. **Claude will execute** the command and load the referenced agent file
3. **Agent activates** following the instructions in their file
4. **Use agent commands** starting with `*` (like `*help`)

## Examples

```
User: /agents
Claude: [Shows all available agents and loading instructions]

User: /bmad/orchestrator  
Claude: [Loads orchestrator, becomes BMad Orchestrator]
        "Hello! I'm the BMad Orchestrator. Type *help to see capabilities."

User: *agent analyst
Claude: [Loads analyst, becomes Mary]
        "Hi! I'm Mary, your Business Analyst. Ready for market research!"

User: *research
Claude: [Executes analyst research capabilities]
```

## File Structure

```
.claude/
├── commands/
│   ├── agents.md              # Show all agents
│   ├── load-agent.md          # Generic agent loader
│   ├── bmad-help.md           # System help
│   └── bmad/                  # Agent namespace
│       ├── orchestrator.md    # Direct orchestrator loading
│       ├── analyst.md         # Direct analyst loading
│       ├── pm.md              # Direct PM loading
│       ├── architect.md       # Direct architect loading
│       └── dev.md             # Direct developer loading
└── README.md                  # This file
```

## Agent Files Referenced

All commands reference agent files in:
`bmad-claude-agents/agents/`

- `bmad-orchestrator.md`
- `business-analyst.md`
- `product-manager.md`
- `architect.md`
- `developer.md`
- `scrum-master.md`
- `qa-engineer.md`
- `ux-expert.md`

## How It Works

1. **Slash Command**: User types `/bmad/dev`
2. **File Reference**: Command file references `@bmad-claude-agents/agents/developer.md`
3. **Agent Loading**: Claude reads the agent file and follows activation instructions
4. **Transformation**: Claude becomes James the Developer
5. **Command Processing**: Claude processes `*` commands as defined in agent file

## Quick Start

Try these commands in Claude Code:

1. `/bmad-help` - See complete system overview
2. `/bmad/orchestrator` - Start with master coordinator
3. `*help` - See orchestrator capabilities
4. `*workflow` - Get workflow guidance

## Benefits

- **Direct Access**: No need to copy/paste agent files
- **Seamless Switching**: Commands handle agent loading automatically
- **Persistent Context**: Agents maintain their personas throughout conversations
- **Workflow Integration**: Orchestrator can guide multi-agent workflows

The BMAD agents are now fully integrated with Claude Code's command system! 🚀