#!/usr/bin/env python3
"""
Simple AI Agent - Integration Example 1

A minimal AI agent demonstrating:
- Hierarchical memory for storing experiences
- Escalation engine for intelligent decision routing
- Learning from interactions

Run: python main.py
"""

import sys
import os
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Try to import from installed packages
    from escalation_engine import (
        EscalationEngine,
        DecisionContext,
        DecisionResult,
        DecisionSource,
        EscalationReason,
    )
    from hierarchical_memory import (
        HierarchicalMemory,
        MemoryType,
        ConsolidationEngine,
    )
except ImportError:
    # If not installed, try to import from local paths
    # This allows running examples without installing packages
    escalation_path = Path(__file__).parent.parent.parent / "escalation-engine"
    memory_path = Path(__file__).parent.parent.parent / "hierarchical-memory"

    if str(escalation_path) not in sys.path:
        sys.path.insert(0, str(escalation_path))
    if str(memory_path / "src") not in sys.path:
        sys.path.insert(0, str(memory_path / "src"))

    from escalation_engine import (
        EscalationEngine,
        DecisionContext,
        DecisionResult,
        DecisionSource,
        EscalationReason,
    )
    from hierarchical_memory import (
        HierarchicalMemory,
        MemoryType,
        ConsolidationEngine,
    )

from shared.utils import (
    load_config,
    print_section,
    print_subsection,
    print_memory,
    print_decision,
    simulate_delay,
)
from shared.mock_llm import MockLLMFactory, LLMProviderType


class SimpleAIAgent:
    """
    A simple AI agent that combines hierarchical memory with
    intelligent decision routing.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the agent.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)

        # Initialize components
        self.memory = HierarchicalMemory(
            character_id="simple_agent",
            config=self.config.get("memory", {}),
        )

        self.escalation = EscalationEngine(
            config_path=config_path,
        )

        # Get LLM provider
        llm_config = self.config.get("llm", {})
        provider_name = llm_config.get("provider", "mock")
        provider_type = LLMProviderType[provider_name.upper()] if provider_name.upper() in LLMProviderType.__members__ else LLMProviderType.OPENAI
        self.llm = MockLLMFactory.get_provider(
            provider=provider_type,
            model=llm_config.get("model", "gpt-4"),
            latency_range=tuple(llm_config.get("latency_range", [100, 400])),
        )

        # Agent state
        self.interaction_count = 0
        self.decisions_made = 0

    def process_input(
        self,
        user_input: str,
        stakes: float = 0.5,
        urgency_ms: Optional[int] = None,
    ) -> str:
        """
        Process user input and generate a response.

        Args:
            user_input: The user's input/query
            stakes: Importance level (0-1)
            urgency_ms: Time constraint in milliseconds

        Returns:
            Agent's response
        """
        self.interaction_count += 1

        # Store in working memory
        self.memory.store_working(
            f"User asked: {user_input[:100]}...",
            importance=4.0,
        )

        # Check for relevant memories
        relevant_memories = self.memory.retrieve(user_input, top_k=3)

        # Route the decision
        context = DecisionContext(
            character_id="simple_agent",
            situation_type="user_query",
            situation_description=user_input,
            stakes=stakes,
            urgency_ms=urgency_ms,
            similar_decisions_count=len(relevant_memories),
        )

        decision = self.escalation.route_decision(context)
        self.decisions_made += 1

        # Generate response based on routing decision
        response = self._generate_response(user_input, decision, relevant_memories)

        # Store the interaction as episodic memory
        self.memory.store_episodic(
            f"Responded to: {user_input[:80]}...",
            importance=5.0 + stakes * 2,
            emotional_valence=0.3,  # Mildly positive
        )

        # Record the decision outcome
        result = DecisionResult(
            decision_id=f"dec_{self.interaction_count}",
            source=decision.source,
            action=response[:100],
            confidence=decision.confidence_required,
            time_taken_ms=50,
            cost_estimate=0.0,
            metadata={"user_input": user_input},
        )
        self.escalation.record_decision(result)
        self.escalation.record_outcome(result.decision_id, success=True)

        return response

    def _generate_response(
        self,
        user_input: str,
        decision,
        relevant_memories: List,
    ) -> str:
        """
        Generate a response based on the routing decision.

        Args:
            user_input: The user's input
            decision: The escalation decision
            relevant_memories: Relevant memories from the past

        Returns:
            Generated response
        """
        # Build context from memories
        memory_context = ""
        if relevant_memories:
            memory_context = " Previous context: " + "; ".join([
                mem.content for mem in relevant_memories[:2]
            ])

        full_prompt = user_input + memory_context

        if decision.source == DecisionSource.BOT:
            # Simple rule-based response
            return self._bot_response(user_input)

        elif decision.source == DecisionSource.BRAIN:
            # Local LLM response
            llm_response = self.llm.complete(full_prompt, temperature=0.7)
            return llm_response.content

        else:  # HUMAN
            # Full API LLM response
            llm_response = self.llm.complete(full_prompt, temperature=0.5)
            return llm_response.content

    def _bot_response(self, user_input: str) -> str:
        """
        Generate a simple rule-based response.

        Args:
            user_input: The user's input

        Returns:
            Rule-based response
        """
        user_input_lower = user_input.lower()

        # Simple pattern matching
        if any(word in user_input_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your AI assistant. How can I help you today?"

        if any(word in user_input_lower for word in ["bye", "goodbye", "see you"]):
            return "Goodbye! Feel free to come back anytime you need assistance."

        if any(word in user_input_lower for word in ["thank", "thanks"]):
            return "You're welcome! Is there anything else I can help with?"

        if any(word in user_input_lower for word in ["who are you", "what are you"]):
            return "I'm a simple AI agent with hierarchical memory and intelligent decision routing."

        if "help" in user_input_lower:
            return "I can help answer questions, remember our conversations, and learn from experience. What would you like to know?"

        # Default response
        return "I understand your query. I'm processing this using my knowledge base. Could you provide more details so I can give you a better response?"

    def reflect_and_consolidate(self) -> None:
        """Run memory consolidation to learn from experience."""
        engine = ConsolidationEngine()

        # Check if consolidation is needed
        if self.memory.should_consolidate_reflection():
            result = engine.consolidate(self.memory, strategy="reflection", force=True)
            print(f"\n  Consolidated {result.output_count} reflection memories")

        if self.memory.should_consolidate_episodic():
            result = engine.consolidate(self.memory, strategy="episodic_semantic", force=True)
            print(f"  Consolidated {result.input_count} episodic memories into {result.output_count} semantic patterns")

    def get_summary(self) -> dict:
        """Get a summary of the agent's state."""
        stats = self.memory.get_stats()
        escalation_stats = self.escalation.get_global_stats()

        return {
            "interactions": self.interaction_count,
            "decisions": self.decisions_made,
            "total_memories": stats.get("total_memories", 0),
            "decisions_by_source": {
                "bot": escalation_stats.get("bot_decisions", 0),
                "brain": escalation_stats.get("brain_decisions", 0),
                "human": escalation_stats.get("human_decisions", 0),
            },
            "llm_stats": self.llm.get_stats(),
        }


def main():
    """Run the simple AI agent example."""
    print_section("Simple AI Agent - Integration Example 1")

    # Initialize agent
    print("Initializing agent...")
    agent = SimpleAIAgent("config.yaml")
    print(f"  Agent ready with {agent.memory.get_stats()['total_memories']} initial memories\n")

    # Example interactions
    interactions = [
        ("Hello! How are you?", 0.1),      # Low stakes - Bot
        ("Can you help me understand something?", 0.3),  # Low-medium stakes
        ("I need to make an important decision about my career path", 0.7),  # High stakes - Brain
        ("What should I do about a complex legal situation I'm in?", 0.9),  # Critical - Human
        ("Thanks for your help!", 0.1),    # Low stakes - Bot
        ("Can you remember what we talked about earlier?", 0.4),  # Medium stakes
    ]

    # Process each interaction
    for i, (user_input, stakes) in enumerate(interactions, 1):
        print_subsection(f"Interaction {i}")

        print(f"  User: {user_input}")
        print(f"  Stakes: {stakes:.1f}")

        simulate_delay(100, 300)

        # Get the decision routing info
        context = DecisionContext(
            character_id="simple_agent",
            situation_type="user_query",
            situation_description=user_input,
            stakes=stakes,
            similar_decisions_count=i - 1,
        )
        decision = agent.escalation.route_decision(context)

        print(f"  Route: {decision.source.value.upper()}")
        print(f"  Reason: {decision.reason.value if decision.reason else 'N/A'}")

        # Get response
        response = agent.process_input(user_input, stakes)
        print(f"  Agent: {response}")

        print()

    # Show summary
    print_section("Agent Summary")

    summary = agent.get_summary()

    print(f"  Total Interactions: {summary['interactions']}")
    print(f"  Total Decisions: {summary['decisions']}")
    print(f"  Total Memories: {summary['total_memories']}")
    print()
    print("  Decisions by Source:")
    for source, count in summary['decisions_by_source'].items():
        print(f"    {source.upper()}: {count}")
    print()
    print("  LLM Usage:")
    llm_stats = summary['llm_stats']
    print(f"    Requests: {llm_stats['request_count']}")
    print(f"    Tokens Used: {llm_stats['total_tokens']}")
    print(f"    Estimated Cost: ${llm_stats['total_cost']:.4f}")

    # Run consolidation
    print()
    print_subsection("Memory Consolidation")
    agent.reflect_and_consolidate()

    # Show important memories
    print()
    print_subsection("Important Memories Learned")
    important = agent.memory.get_important(threshold=5.0, top_k=5)
    for mem in important:
        print_memory(mem)

    # Generate narrative
    print()
    print_subsection("Agent's Experience Narrative")
    narrative = agent.memory.generate_narrative()
    print(f"  Coherence Score: {narrative.coherence_score:.2f}")
    print(f"  Key Themes: {', '.join(narrative.key_themes)}")
    print()
    print("  Narrative:")
    for line in narrative.narrative.split("\n")[:5]:
        print(f"    {line}")

    print()
    print_section("Example Complete!")
    print()


if __name__ == "__main__":
    main()
