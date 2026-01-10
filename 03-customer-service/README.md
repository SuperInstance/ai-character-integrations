# Example 3: Customer Service Bot

A support agent demonstrating tiered escalation, customer interaction memory, and cost optimization.

## What This Example Shows

- Tiered support escalation (FAQ -> Bot -> Human)
- Memory of customer interactions across sessions
- Cost tracking and optimization
- Sentiment-aware responses
- Learning from resolved tickets

## Architecture

```
Customer Query
       │
       ▼
┌──────────────────┐
│ Sentiment Analysis│
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         Escalation Engine                    │
├─────────────────────────────────────────────┤
│  Level 1: FAQ/Bot (Free)                    │
│  Level 2: Brain LLM (Low cost)              │
│  Level 3: Human Agent (High cost)           │
└────────────────────┬────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │   Response   │
              │  Generator   │
              └──────────────┘
```

## Running the Example

```bash
# From the integration-examples directory
cd 03-customer-service
python main.py
```

## Features

### Tier 1: Bot/FAQ (Free)
- Handles common questions instantly
- Pre-written responses for known issues
- 100% automated, zero cost

### Tier 2: Brain (Local LLM)
- Handles novel but non-critical queries
- Uses customer history for context
- Low incremental cost

### Tier 3: Human (API LLM)
- Complex or sensitive issues
- High-value customers
- Critical account issues

## Configuration

Edit `config.yaml` to customize:
- Tier thresholds
- Cost tracking settings
- Bot response rules
- Sentiment weights

## Metrics Tracked

- Total queries handled
- Queries per tier
- Cost savings vs. all-human
- Average resolution time
- Customer satisfaction (simulated)
