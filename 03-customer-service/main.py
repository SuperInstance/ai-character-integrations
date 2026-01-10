#!/usr/bin/env python3
"""
Customer Service Bot - Integration Example 3

A support agent demonstrating:
- Tiered support escalation (FAQ -> Bot -> Human)
- Customer interaction memory
- Cost tracking and optimization
- Sentiment-aware responses

Run: python main.py
"""

import sys
import os
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory, ConsolidationEngine
except ImportError:
    escalation_path = Path(__file__).parent.parent.parent / "escalation-engine"
    memory_path = Path(__file__).parent.parent.parent / "hierarchical-memory"

    if str(escalation_path) not in sys.path:
        sys.path.insert(0, str(escalation_path))
    if str(memory_path / "src") not in sys.path:
        sys.path.insert(0, str(memory_path / "src"))

    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory, ConsolidationEngine

from bot_rules import BotRulesEngine, get_bot_engine
from shared.utils import (
    load_config,
    print_section,
    print_subsection,
    simulate_delay,
)
from shared.mock_llm import MockLLMFactory, LLMProviderType


@dataclass
class Customer:
    """Customer information."""
    customer_id: str
    name: str
    email: str
    tier: str = "standard"  # standard, premium, enterprise
    account_value: float = 0.0
    previous_issues: List[str] = field(default_factory=list)
    satisfaction_score: float = 0.5  # 0-1


@dataclass
class Ticket:
    """A support ticket."""
    ticket_id: str
    customer_id: str
    query: str
    category: str
    priority: str  # low, medium, high, critical
    status: str = "open"
    resolution: Optional[str] = None
    cost: float = 0.0
    tier_handled: Optional[str] = None
    sentiment: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)


class SentimentAnalyzer:
    """Simple sentiment analyzer for customer queries."""

    # Keywords for sentiment analysis
    NEGATIVE_WORDS = {
        "angry", "frustrated", "terrible", "horrible", "awful", "hate",
        "worst", "disappointed", "upset", "unhappy", "annoyed", "furious",
        "ridiculous", "unacceptable", "useless", "incompetent", "stupid",
    }

    POSITIVE_WORDS = {
        "great", "good", "excellent", "happy", "love", "thank", "thanks",
        "helpful", "appreciate", "wonderful", "amazing", "perfect", "easy",
    }

    URGENT_WORDS = {
        "urgent", "emergency", "asap", "immediately", "critical", "important",
        "deadline", "broken", "down", "can't work", "not working",
    }

    @classmethod
    def analyze(cls, text: str) -> Tuple[float, float, List[str]]:
        """
        Analyze sentiment of text.

        Returns:
            (sentiment_score, urgency_score, keywords_found)
            sentiment: -1 (negative) to 1 (positive)
            urgency: 0 to 1
        """
        text_lower = text.lower()
        words = set(text_lower.split())

        # Sentiment scoring
        negative_count = sum(1 for w in words if w in cls.NEGATIVE_WORDS)
        positive_count = sum(1 for w in words if w in cls.POSITIVE_WORDS)

        sentiment = (positive_count - negative_count) / max(1, positive_count + negative_count)

        # Urgency scoring
        urgency_count = sum(1 for w in words if w in cls.URGENT_WORDS)
        urgency = min(1.0, urgency_count * 0.3)

        keywords_found = [w for w in words if w in cls.NEGATIVE_WORDS or w in cls.POSITIVE_WORDS or w in cls.URGENT_WORDS]

        return sentiment, urgency, keywords_found


class CustomerServiceBot:
    """
    Customer service bot with tiered escalation and memory.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the bot."""
        self.config = load_config(config_path)

        # Initialize components
        self.memory = HierarchicalMemory(
            character_id="customer_service_bot",
            config=self.config.get("memory", {}),
        )

        self.escalation = EscalationEngine()
        self.bot_rules = get_bot_engine()
        self.llm = MockLLMFactory.get_provider()

        # Customer database
        self.customers: Dict[str, Customer] = {}
        self.tickets: List[Ticket] = []

        # Metrics
        self.queries_handled = 0
        self.total_cost = 0.0

    def get_or_create_customer(
        self,
        customer_id: str,
        name: str = "",
        email: str = "",
        tier: str = "standard",
    ) -> Customer:
        """Get or create a customer."""
        if customer_id not in self.customers:
            self.customers[customer_id] = Customer(
                customer_id=customer_id,
                name=name or f"Customer {customer_id}",
                email=email or f"{customer_id}@example.com",
                tier=tier,
            )
        return self.customers[customer_id]

    def calculate_stakes(
        self,
        customer: Customer,
        query: str,
        sentiment: float,
        urgency: float,
    ) -> float:
        """Calculate stakes level for escalation."""
        config = self.config.get("escalation", {})
        cost_config = self.config.get("cost_tracking", {})

        # Base stakes from urgency
        stakes = urgency

        # Adjust based on customer tier
        tier_boost = {
            "standard": 0.0,
            "premium": 0.1,
            "enterprise": 0.15,
        }
        stakes += tier_boost.get(customer.tier, 0.0)

        # Adjust based on sentiment (negative = higher stakes)
        if sentiment < 0:
            stakes += abs(sentiment) * 0.3

        # Check for critical keywords
        critical_keywords = self.config.get("sentiment", {}).get("critical_keywords", [])
        query_lower = query.lower()
        if any(re.search(pattern, query_lower) for pattern in critical_keywords):
            stakes += 0.3

        # Previous issues increase stakes
        if len(customer.previous_issues) > 3:
            stakes += 0.1

        return min(1.0, stakes)

    def handle_query(
        self,
        customer_id: str,
        query: str,
        customer_name: str = "",
        customer_email: str = "",
        customer_tier: str = "standard",
    ) -> Ticket:
        """
        Handle a customer query.

        Returns:
            Created ticket with resolution
        """
        self.queries_handled += 1

        # Get customer
        customer = self.get_or_create_customer(
            customer_id,
            customer_name,
            customer_email,
            customer_tier,
        )

        # Analyze sentiment
        sentiment, urgency, keywords = SentimentAnalyzer.analyze(query)

        # Calculate stakes
        stakes = self.calculate_stakes(customer, query, sentiment, urgency)

        # Check bot rules first
        handled, bot_response, confidence = self.bot_rules.get_response(
            query,
            min_confidence=self.config["escalation"]["bot_min_confidence"],
        )

        # Determine category
        category = self._categorize_query(query)

        # Determine priority
        priority = self._determine_priority(stakes, urgency, customer.tier)

        # Create ticket
        ticket = Ticket(
            ticket_id=f"TKT-{self.queries_handled:05d}",
            customer_id=customer_id,
            query=query,
            category=category,
            priority=priority,
            sentiment=sentiment,
        )

        # Handle based on rules and escalation
        if handled and stakes <= self.config["escalation"]["bot_max_stakes"]:
            # Bot can handle it
            ticket.resolution = bot_response
            ticket.tier_handled = "BOT"
            ticket.cost = self.config["cost_tracking"]["bot_cost"]
        else:
            # Need to escalate
            context = DecisionContext(
                character_id=customer_id,
                situation_type=f"customer_service_{category}",
                situation_description=query,
                stakes=stakes,
                urgency_ms=int(2000 / (stakes + 0.5)),  # Higher stakes = faster
            )

            decision = self.escalation.route_decision(context)

            if decision.source == DecisionSource.BOT and stakes > 0.5:
                # Escalation said bot, but stakes are moderate
                # Try brain for better quality
                ticket.tier_handled = "BRAIN"
                ticket.cost = self.config["cost_tracking"]["brain_cost"]
                ticket.resolution = self._get_llm_response(query, customer, temperature=0.7)

            elif decision.source == DecisionSource.BRAIN:
                ticket.tier_handled = "BRAIN"
                ticket.cost = self.config["cost_tracking"]["brain_cost"]
                ticket.resolution = self._get_llm_response(query, customer, temperature=0.7)

            else:  # HUMAN
                ticket.tier_handled = "HUMAN"
                ticket.cost = self.config["cost_tracking"]["human_cost"]
                ticket.resolution = self._get_llm_response(query, customer, temperature=0.5)

        ticket.status = "resolved"
        self.total_cost += ticket.cost
        self.tickets.append(ticket)

        # Store in memory
        self._store_interaction(customer, query, ticket, sentiment)

        # Record decision
        result = DecisionResult(
            decision_id=ticket.ticket_id,
            source=DecisionSource[ticket.tier_handled] if ticket.tier_handled else DecisionSource.BOT,
            action=ticket.resolution[:100],
            confidence=confidence,
            time_taken_ms=50 if ticket.tier_handled == "BOT" else 500,
            cost_estimate=ticket.cost,
        )
        self.escalation.record_decision(result)
        self.escalation.record_outcome(result.decision_id, success=True)

        # Track issue for customer
        customer.previous_issues.append(query)

        return ticket

    def _categorize_query(self, query: str) -> str:
        """Categorize the query."""
        query_lower = query.lower()

        categories = {
            "account": ["account", "login", "password", "sign", "register"],
            "billing": ["bill", "payment", "charge", "invoice", "refund", "cost"],
            "technical": ["error", "bug", "crash", "slow", "broken", "work"],
            "feature": ["feature", "function", "how to", "can i"],
            "sales": ["price", "plan", "upgrade", "subscription"],
        }

        for category, keywords in categories.items():
            if any(kw in query_lower for kw in keywords):
                return category

        return "general"

    def _determine_priority(self, stakes: float, urgency: float, tier: str) -> str:
        """Determine ticket priority."""
        if stakes >= 0.8 or urgency >= 0.7 or tier == "enterprise":
            return "critical"
        elif stakes >= 0.6 or urgency >= 0.5 or tier == "premium":
            return "high"
        elif stakes >= 0.3:
            return "medium"
        else:
            return "low"

    def _get_llm_response(self, query: str, customer: Customer, temperature: float) -> str:
        """Get LLM response."""
        prompt = f"Customer query: {query}\n"

        if customer.tier != "standard":
            prompt += f"Customer is {customer.tier} tier.\n"

        if customer.previous_issues:
            prompt += f"Previous issues: {len(customer.previous_issues)}.\n"

        response = self.llm.complete(prompt, temperature=temperature)
        return response.content

    def _store_interaction(self, customer: Customer, query: str, ticket: Ticket, sentiment: float) -> None:
        """Store interaction in memory."""
        self.memory.store_episodic(
            f"Customer {customer.name} (ID: {customer.customer_id}): {query[:100]}...",
            importance=5.0 + ticket.priority_weight(),
            emotional_valence=sentiment,
            participants=[customer.name],
        )

    def get_stats(self) -> Dict:
        """Get bot statistics."""
        tier_counts = {"BOT": 0, "BRAIN": 0, "HUMAN": 0}
        for t in self.tickets:
            if t.tier_handled:
                tier_counts[t.tier_handled] += 1

        # Calculate cost savings
        all_human_cost = len(self.tickets) * self.config["cost_tracking"]["human_cost"]
        savings = all_human_cost - self.total_cost
        savings_percent = (savings / all_human_cost * 100) if all_human_cost > 0 else 0

        return {
            "queries_handled": self.queries_handled,
            "total_cost": round(self.total_cost, 4),
            "all_human_cost": round(all_human_cost, 4),
            "savings": round(savings, 4),
            "savings_percent": round(savings_percent, 1),
            "tier_distribution": tier_counts,
            "avg_cost_per_query": round(self.total_cost / max(1, self.queries_handled), 4),
        }


# Add priority weight to Ticket
def priority_weight(self) -> float:
    """Calculate priority weight for importance."""
    weights = {"low": 1.0, "medium": 2.0, "high": 3.0, "critical": 4.0}
    return weights.get(self.priority, 2.0)


Ticket.priority_weight = priority_weight


def simulate_customer_queries(bot: CustomerServiceBot) -> None:
    """Simulate various customer queries."""
    queries = [
        # Low stakes - Bot
        ("CUST001", "Alice Johnson", "alice@example.com", "standard",
         "Hi, I need to reset my password. Can you help?"),

        ("CUST002", "Bob Smith", "bob@example.com", "standard",
         "What are your pricing plans?"),

        ("CUST003", "Carol White", "carol@example.com", "standard",
         "Thank you for your help!"),

        # Medium stakes - Brain
        ("CUST004", "David Brown", "david@example.com", "premium",
         "I'm having trouble accessing the export feature. It says 'loading' but nothing happens."),

        ("CUST005", "Eve Davis", "eve@example.com", "standard",
         "I was charged twice this month. Can you look into this?"),

        # High stakes - Brain/Human
        ("CUST006", "Frank Miller", "frank@example.com", "premium",
         "I'm really frustrated. The system has been down for 2 hours and I can't process orders."),

        # Critical - Human
        ("CUST007", "Grace Lee", "grace@example.com", "enterprise",
         "This is unacceptable. I'm losing money every minute this is down. I need to speak to a manager immediately."),

        ("CUST008", "Henry Wilson", "henry@example.com", "standard",
         "I want a refund for my entire annual subscription. This service is terrible."),

        # More bot queries
        ("CUST009", "Ivy Chen", "ivy@example.com", "standard",
         "How do I change my email address?"),

        ("CUST010", "Jack Taylor", "jack@example.com", "standard",
         "What are your support hours?"),
    ]

    for customer_id, name, email, tier, query in queries:
        simulate_delay(50, 150)

        print_subsection(f"Query from {name}")

        # Analyze sentiment
        sentiment, urgency, keywords = SentimentAnalyzer.analyze(query)
        print(f"  Query: {query[:80]}...")
        print(f"  Sentiment: {sentiment:+.2f} | Urgency: {urgency:.2f}")
        if keywords:
            print(f"  Keywords: {', '.join(keywords)}")

        # Handle query
        ticket = bot.handle_query(customer_id, query, name, email, tier)

        print(f"  Tier: {ticket.tier_handled} | Priority: {ticket.priority} | Cost: ${ticket.cost:.4f}")
        print(f"  Response: {ticket.resolution[:120]}...")
        print()


def main():
    """Main entry point."""
    print_section("Customer Service Bot - Integration Example 3")

    # Initialize bot
    bot = CustomerServiceBot("config.yaml")

    print("Bot initialized with the following capabilities:")
    stats = bot.bot_rules.get_stats()
    print(f"  - {stats['total_rules']} FAQ rules covering {len(stats['categories'])} categories")
    print(f"  - Hierarchical memory for customer history")
    print(f"  - Tiered escalation for cost optimization")
    print()

    # Simulate queries
    print_section("Processing Customer Queries")
    simulate_customer_queries(bot)

    # Show statistics
    print_section("Bot Performance Statistics")

    stats = bot.get_stats()
    print(f"  Total Queries Handled: {stats['queries_handled']}")
    print(f"  Total Cost: ${stats['total_cost']:.2f}")
    print(f"  Cost if All Human: ${stats['all_human_cost']:.2f}")
    print(f"  Savings: ${stats['savings']:.2f} ({stats['savings_percent']:.1f}%)")
    print(f"  Avg Cost Per Query: ${stats['avg_cost_per_query']:.4f}")
    print()
    print("  Tier Distribution:")
    for tier, count in stats['tier_distribution'].items():
        percent = (count / stats['queries_handled'] * 100) if stats['queries_handled'] > 0 else 0
        print(f"    {tier}: {count} ({percent:.1f}%)")

    # Show tickets by priority
    print()
    print_subsection("Tickets by Priority")
    priority_counts = {}
    for t in bot.tickets:
        priority_counts[t.priority] = priority_counts.get(t.priority, 0) + 1
    for priority, count in sorted(priority_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {priority.title()}: {count}")

    # Show escalation engine stats
    print()
    print_subsection("Escalation Engine Stats")
    e_stats = bot.escalation.get_global_stats()
    print(f"  Total Decisions: {e_stats['total_decisions']}")
    print(f"  Bot Decisions: {e_stats['bot_decisions']}")
    print(f"  Brain Decisions: {e_stats['brain_decisions']}")
    print(f"  Human Decisions: {e_stats['human_decisions']}")
    print(f"  Success Rate: {e_stats['success_rate']:.1%}")

    # Show some memories
    print()
    print_subsection("Sample Customer Memories")
    memories = bot.memory.get_important(threshold=5.0, top_k=3)
    for mem in memories:
        print(f"  [{mem.importance:.1f}] {mem.content[:80]}...")

    print()
    print_section("Example Complete!")


if __name__ == "__main__":
    main()
