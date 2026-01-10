#!/usr/bin/env python3
"""
Learning Loop - Integration Example 5

A complete pipeline demonstrating:
- Training data collection
- Experience replay
- Memory consolidation
- Learning and adaptation
- Performance evaluation

Run: python main.py
"""

import sys
import random
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from training import (
    LearningLoop,
    ExperienceOutcome,
    DecisionSource,
    Experience,
)
from shared.utils import print_section, print_subsection, simulate_delay


# Simulated environment for generating experiences
class SimulatedEnvironment:
    """
    Simulated environment that generates scenarios for learning.

    This mimics real-world interactions that would produce experiences.
    """

    def __init__(self):
        """Initialize the environment."""
        self.scenario_templates = {
            "customer_support": [
                ("Password reset request", 0.1, 0.9, DecisionSource.BOT),
                ("Complex billing inquiry", 0.5, 0.7, DecisionSource.BRAIN),
                ("Angry customer demanding refund", 0.9, 0.5, DecisionSource.HUMAN),
                ("Product feature question", 0.2, 0.85, DecisionSource.BOT),
                ("Technical troubleshooting", 0.6, 0.65, DecisionSource.BRAIN),
            ],
            "game_ai": [
                ("Navigate to target", 0.3, 0.8, DecisionSource.BOT),
                ("Combat encounter with weak enemy", 0.4, 0.75, DecisionSource.BRAIN),
                ("Boss battle with low health", 0.95, 0.4, DecisionSource.HUMAN),
                ("Puzzle solving", 0.5, 0.7, DecisionSource.BRAIN),
                ("Inventory management", 0.1, 0.95, DecisionSource.BOT),
            ],
            "personal_assistant": [
                ("Set a reminder", 0.1, 0.98, DecisionSource.BOT),
                ("Answer factual question", 0.3, 0.85, DecisionSource.BOT),
                ("Complex scheduling negotiation", 0.7, 0.6, DecisionSource.BRAIN),
                ("Emotional support request", 0.8, 0.5, DecisionSource.HUMAN),
            ],
        }

    def get_scenario(self) -> Tuple[str, str, float, float, DecisionSource]:
        """
        Generate a random scenario.

        Returns:
            (situation_type, description, stakes, success_probability, ideal_source)
        """
        situation_type = random.choice(list(self.scenario_templates.keys()))
        scenarios = self.scenario_templates[situation_type]
        description, stakes, success_prob, ideal_source = random.choice(scenarios)
        return situation_type, description, stakes, success_prob, ideal_source

    def simulate_outcome(
        self,
        decision_source: DecisionSource,
        ideal_source: DecisionSource,
        success_probability: float,
    ) -> Tuple[ExperienceOutcome, float]:
        """
        Simulate the outcome of a decision.

        Returns:
            (outcome, reward)
        """
        # Match decision to ideal source
        if decision_source == ideal_source:
            # Correct routing
            if random.random() < success_probability:
                return ExperienceOutcome.SUCCESS, random.uniform(0.5, 1.0)
            else:
                return ExperienceOutcome.PARTIAL, random.uniform(0.0, 0.5)
        elif decision_source == DecisionSource.BOT and ideal_source == DecisionSource.BRAIN:
            # Under-routed (bot when should be brain)
            if random.random() < success_probability * 0.7:
                return ExperienceOutcome.PARTIAL, random.uniform(0.0, 0.3)
            else:
                return ExperienceOutcome.FAILURE, random.uniform(-0.5, 0.0)
        elif decision_source == DecisionSource.BRAIN and ideal_source == DecisionSource.HUMAN:
            # Under-routed (brain when should be human)
            if random.random() < success_probability * 0.6:
                return ExperienceOutcome.PARTIAL, random.uniform(0.0, 0.3)
            else:
                return ExperienceOutcome.FAILURE, random.uniform(-0.5, -0.1)
        else:
            # Over-routed (more expensive than needed, but should work)
            return ExperienceOutcome.SUCCESS, random.uniform(0.3, 0.7)


def demonstrate_learning_cycle(learning_loop: LearningLoop, num_experiences: int = 50) -> None:
    """Demonstrate a complete learning cycle."""
    print_subsection(f"Collecting {num_experiences} Experiences")

    env = SimulatedEnvironment()

    for i in range(num_experiences):
        # Get a scenario
        situation_type, description, stakes, success_prob, ideal_source = env.get_scenario()

        # Make a decision (using escalation engine)
        from escalation_engine import DecisionContext
        context = DecisionContext(
            character_id="learning_agent",
            situation_type=situation_type,
            situation_description=description,
            stakes=stakes,
        )
        decision = learning_loop.escalation.route_decision(context)

        # Simulate outcome
        outcome, reward = env.simulate_outcome(decision.source, ideal_source, success_prob)

        # Add experience to learning loop
        learning_loop.add_experience(
            situation_type=situation_type,
            situation_description=description,
            decision_source=decision.source,
            action_taken=f"Routed to {decision.source.value}",
            outcome=outcome,
            reward=reward,
            context={"stakes": stakes, "ideal_source": ideal_source.value},
        )

        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Collected {i + 1}/{num_experiences} experiences...")

    print()


def demonstrate_replay(learning_loop: LearningLoop) -> None:
    """Demonstrate experience replay."""
    print_subsection("Experience Replay")

    batch, updates = learning_loop.run_replay_cycle()

    print(f"  Batch Size: {len(batch.experiences)} experiences")
    print(f"  Batch Success Rate: {batch.get_success_rate():.1%}")
    print(f"  Batch Average Reward: {batch.get_avg_reward():+.2f}")

    if updates:
        print()
        print("  Threshold Updates:")
        for key, value in updates.items():
            print(f"    {key}: {value:.3f}")

    print()


def demonstrate_consolidation(learning_loop: LearningLoop) -> None:
    """Demonstrate memory consolidation."""
    print_subsection("Memory Consolidation")

    results = learning_loop.consolidate_memories()

    print(f"  Reflection patterns: {results['reflection']}")
    print(f"  Episodic patterns: {results['episodic_semantic']}")
    print(f"  Total new patterns: {results['total']}")
    print()


def demonstrate_evaluation(learning_loop: LearningLoop) -> None:
    """Demonstrate performance evaluation."""
    print_subsection("Performance Evaluation")

    eval_data = learning_loop.evaluate()

    print(f"  Total Experiences: {eval_data['total_experiences']}")
    print(f"  Overall Success Rate: {eval_data['success_rate']:.1%}")
    print(f"  Recent Success Rate: {eval_data['recent_success_rate']:.1%}")
    print(f"  Average Reward: {eval_data['avg_reward']:+.2f}")
    print()
    print("  Decision Distribution:")
    for source, count in eval_data['decision_distribution'].items():
        total = eval_data['total_experiences']
        pct = (count / total * 100) if total > 0 else 0
        print(f"    {source.upper()}: {count} ({pct:.1f}%)")
    print()
    print("  Current Adaptive Thresholds:")
    for name, value in eval_data['current_thresholds'].items():
        print(f"    {name}: {value:.3f}")


def show_learning_progress(learning_loop: LearningLoop) -> None:
    """Show learning progress over time."""
    print_subsection("Learning Progress")

    if learning_loop.metrics.success_rate_history:
        history = learning_loop.metrics.success_rate_history
        print(f"  Success Rate Progression:")
        for i, rate in enumerate(history[::10]):  # Every 10th
            epoch = (i + 1) * 10
            print(f"    Epoch {epoch:3d}: {rate:.1%}")

    if learning_loop.learner.threshold_history:
        print()
        print("  Threshold Adaptation:")
        for entry in learning_loop.learner.threshold_history[-5:]:
            print(f"    Bot: {entry['bot_threshold']:.2f} | "
                  f"Brain: {entry['brain_threshold']:.2f} | "
                  f"Success: {entry['success_rate']:.1%}")

    print()


def show_learned_patterns(learning_loop: LearningLoop) -> None:
    """Show patterns learned from consolidation."""
    print_subsection("Learned Patterns")

    semantic = learning_loop.memory.get_important(threshold=5.0, top_k=5)

    if not semantic:
        print("  No significant patterns learned yet.")
        print("  (Need more experiences or consolidation)")
    else:
        for mem in semantic[:5]:
            print(f"  [{mem.importance:.1f}] {mem.content[:70]}...")

    print()


def main():
    """Main entry point."""
    print_section("Learning Loop - Integration Example 5")

    # Initialize learning loop
    print("Initializing learning loop...")
    learning_loop = LearningLoop("config.yaml")
    print("  Components ready:")
    print("    - Experience Collector")
    print("    - Experience Replay Buffer")
    print("    - Adaptive Learner")
    print("    - Memory Consolidation Engine")
    print("    - Performance Evaluator")
    print()

    # Phase 1: Initial learning
    print_section("Phase 1: Initial Training (50 experiences)")
    demonstrate_learning_cycle(learning_loop, num_experiences=50)
    demonstrate_evaluation(learning_loop)
    simulate_delay()

    # Phase 2: Replay and consolidation
    print_section("Phase 2: Experience Replay and Consolidation")
    demonstrate_replay(learning_loop)
    demonstrate_consolidation(learning_loop)
    show_learned_patterns(learning_loop)
    simulate_delay()

    # Phase 3: Continued learning
    print_section("Phase 3: Continued Learning (50 more experiences)")
    demonstrate_learning_cycle(learning_loop, num_experiences=50)
    demonstrate_evaluation(learning_loop)
    simulate_delay()

    # Phase 4: Another consolidation cycle
    print_section("Phase 4: Second Consolidation Cycle")
    demonstrate_replay(learning_loop)
    demonstrate_consolidation(learning_loop)
    simulate_delay()

    # Final report
    print_section("Final Learning Report")
    show_learning_progress(learning_loop)
    show_learned_patterns(learning_loop)

    # Generate full report
    print()
    print(learning_loop.generate_report())

    # Show memory stats
    print()
    print_subsection("Memory System Stats")
    stats = learning_loop.memory.get_stats()
    print(f"  Total Memories: {stats.get('total_memories', 0)}")
    print(f"  Memory Types:")
    for mtype, mtype_stats in stats.get('by_type', {}).items():
        print(f"    {mtype}: {mtype_stats.get('count', 0)}")

    print()
    print_section("Learning Loop Complete!")
    print()
    print("Key Takeaways:")
    print("  1. Experience collection captures all interactions")
    print("  2. Replay allows learning from past experiences")
    print("  3. Consolidation extracts patterns from episodic memories")
    print("  4. Adaptive thresholds improve over time")
    print("  5. Performance metrics track progress continuously")
    print()


if __name__ == "__main__":
    main()
