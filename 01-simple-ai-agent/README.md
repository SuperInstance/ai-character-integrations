# Example 1: Simple AI Agent

A minimal example demonstrating how to build an AI agent with hierarchical memory and intelligent decision routing.

## What This Example Shows

- Creating an AI agent with hierarchical memory
- Using the escalation engine to route decisions
- Storing and retrieving memories
- Learning from experience

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Simple AI Agent                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Escalation │      │  Hierarchical│                     │
│  │     Engine   │◄─────┤    Memory    │                     │
│  │              │      │              │                     │
│  │ Routes to:   │      │ - Working    │                     │
│  │ - Bot        │      │ - Episodic   │                     │
│  │ - Brain      │      │ - Semantic   │                     │
│  │ - Human      │      │ - Procedural │                     │
│  └──────────────┘      └──────────────┘                     │
│           │                      │                           │
│           └──────────┬───────────┘                           │
│                      ▼                                       │
│              ┌──────────────┐                               │
│              │   Response   │                               │
│              │  Generator   │                               │
│              └──────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

## Running the Example

```bash
# From the integration-examples directory
cd 01-simple-ai-agent
python main.py
```

## Expected Output

The agent will:
1. Initialize with empty memory
2. Process several user queries
3. Route decisions based on complexity
4. Learn from interactions
5. Generate a summary of its experience

## Configuration

Edit `config.yaml` to customize:
- Escalation thresholds
- Memory limits
- LLM settings

## Use Cases

This pattern is suitable for:
- Simple chatbots
- Virtual assistants
- Customer support automation
- Information retrieval agents
