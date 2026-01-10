# WebSocket Fabric - Integration Examples

Comprehensive integration examples demonstrating how to combine the standalone tools from the WebSocket Fabric ecosystem.

## Available Tools

| Tool | Language | Description |
|------|----------|-------------|
| [escalation-engine](../escalation-engine) | Python | Intelligent decision routing with 40x cost reduction |
| [hierarchical-memory](../hierarchical-memory) | Python | 6-tier memory system for AI agents |
| [ws-status-indicator](../ws-status-indicator) | TypeScript/React | WebSocket status indicator with auto-reconnection |

## Examples

### Python Examples

| Example | Description | Tools Used |
|---------|-------------|------------|
| [01-simple-ai-agent](./01-simple-ai-agent/) | Basic AI agent with memory and decision routing | escalation-engine, hierarchical-memory |
| [02-dnd-character](./02-dnd-character/) | Full RPG character with learning and personality | escalation-engine, hierarchical-memory |
| [03-customer-service](./03-customer-service/) | Support agent with smart escalation | escalation-engine, hierarchical-memory |
| [04-multi-agent](./04-multi-agent/) | Coordinated multi-agent system | escalation-engine, hierarchical-memory |
| [05-learning-loop](./05-learning-loop/) | Complete training data pipeline | escalation-engine, hierarchical-memory |

### TypeScript/React Examples

| Example | Description | Tools Used |
|---------|-------------|------------|
| [06-react-dashboard](./06-react-dashboard/) | Real-time dashboard with WebSocket status | ws-status-indicator |

## Quick Start

### Prerequisites

```bash
# Python 3.9+
python --version

# Node.js 18+ (for React examples)
node --version
```

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/websocket-fabric
cd websocket-fabric/integration-examples

# Install Python dependencies
pip install -r requirements.txt

# Install React dependencies (for React examples)
cd 06-react-dashboard
npm install
cd ..
```

### Running Examples

#### Python Examples

```bash
# Simple AI Agent
python 01-simple-ai-agent/main.py

# D&D Character
python 02-dnd-character/main.py

# Customer Service Bot
python 03-customer-service/main.py

# Multi-Agent Team
python 04-multi-agent/main.py

# Learning Loop
python 05-learning-loop/main.py
```

#### React Example

```bash
cd 06-react-dashboard
npm run dev
```

## Example Scenarios

### 1. Simple AI Agent

A minimal example showing:
- Creating an AI agent with hierarchical memory
- Routing decisions through the escalation engine
- Storing and retrieving memories
- Basic learning from experience

**Use case:** Chatbots, virtual assistants, simple automation

### 2. D&D Character

A complete RPG character demonstrating:
- Personality-driven decisions
- Memory of adventures and NPCs
- Learning from combat and social encounters
- Identity persistence across sessions

**Use case:** Game AI, interactive fiction, role-playing games

### 3. Customer Service Bot

A support agent featuring:
- Tiered support escalation (FAQ -> human)
- Memory of customer interactions
- Cost tracking and optimization
- Sentiment-aware responses

**Use case:** Customer support, helpdesk automation

### 4. Multi-Agent Team

A coordinated system showing:
- Multiple specialized agents
- Inter-agent communication
- Shared knowledge base
- Task delegation

**Use case:** Enterprise automation, workflow orchestration

### 5. Learning Loop

A complete pipeline demonstrating:
- Training data collection
- Experience replay
- Model refinement
- Performance tracking

**Use case:** AI training, reinforcement learning, data pipelines

### 6. React Dashboard

A real-time dashboard with:
- WebSocket connection management
- Auto-reconnection with exponential backoff
- Status indicators
- Message handling

**Use case:** Real-time applications, live dashboards, chat apps

## Architecture

```
integration-examples/
+-- 01-simple-ai-agent/
|   +-- main.py
|   +-- config.yaml
|   +-- README.md
+-- 02-dnd-character/
|   +-- main.py
|   +-- character.py
|   +-- config.yaml
|   +-- README.md
+-- 03-customer-service/
|   +-- main.py
|   +-- bot_rules.py
|   +-- config.yaml
|   +-- README.md
+-- 04-multi-agent/
|   +-- main.py
|   +-- agents.py
|   +-- coordinator.py
|   +-- config.yaml
|   +-- README.md
+-- 05-learning-loop/
|   +-- main.py
|   +-- training.py
|   +-- config.yaml
|   +-- README.md
+-- 06-react-dashboard/
|   +-- src/
|   +-- package.json
|   +-- README.md
+-- shared/
|   +-- mock_llm.py
|   +-- utils.py
+-- requirements.txt
+-- README.md
```

## Development

### Adding a New Example

1. Create a new directory: `mkdir -p XX-example-name`
2. Add a `README.md` describing the example
3. Add the main code file
4. Update this README with the new example

### Testing

```bash
# Run all Python examples
python -m pytest tests/

# Run specific example tests
python -m pytest tests/test_simple_agent.py
```

## Contributing

Contributions welcome! Please read our contributing guidelines.

## License

MIT License - see LICENSE file for details.

## Links

- [escalation-engine](../escalation-engine/README.md) - Decision routing
- [hierarchical-memory](../hierarchical-memory/README.md) - Memory system
- [ws-status-indicator](../ws-status-indicator/README.md) - WebSocket status
