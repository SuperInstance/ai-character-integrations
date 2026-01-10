"""
Training and Learning Loop Implementation

Implements the complete learning pipeline:
1. Experience Collection
2. Experience Replay
3. Memory Consolidation
4. Learning and Adaptation
5. Performance Evaluation
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
from datetime import datetime, timedelta
import json

try:
    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory, ConsolidationEngine
except ImportError:
    import sys
    from pathlib import Path

    escalation_path = Path(__file__).parent.parent.parent / "escalation-engine"
    memory_path = Path(__file__).parent.parent.parent / "hierarchical-memory"

    if str(escalation_path) not in sys.path:
        sys.path.insert(0, str(escalation_path))
    if str(memory_path / "src") not in sys.path:
        sys.path.insert(0, str(memory_path / "src"))

    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory, ConsolidationEngine


class ExperienceOutcome(Enum):
    """Possible outcomes of an experience."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass
class Experience:
    """A single experience for learning."""

    experience_id: str
    timestamp: datetime
    situation_type: str
    situation_description: str
    decision_source: DecisionSource
    action_taken: str
    outcome: ExperienceOutcome
    reward: float  # Positive for good, negative for bad
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "experience_id": self.experience_id,
            "timestamp": self.timestamp.isoformat(),
            "situation_type": self.situation_type,
            "situation_description": self.situation_description,
            "decision_source": self.decision_source.value,
            "action_taken": self.action_taken,
            "outcome": self.outcome.value,
            "reward": self.reward,
            "context": self.context,
            "metadata": self.metadata,
        }


@dataclass
class ReplayBatch:
    """A batch of experiences for replay."""
    experiences: List[Experience]
    batch_id: str
    timestamp: datetime = field(default_factory=datetime.now)

    def get_avg_reward(self) -> float:
        """Get average reward of the batch."""
        if not self.experiences:
            return 0.0
        return sum(e.reward for e in self.experiences) / len(self.experiences)

    def get_success_rate(self) -> float:
        """Get success rate of the batch."""
        if not self.experiences:
            return 0.0
        successes = sum(1 for e in self.experiences if e.outcome == ExperienceOutcome.SUCCESS)
        return successes / len(self.experiences)


@dataclass
class LearningMetrics:
    """Metrics tracking learning progress."""

    total_experiences: int = 0
    successful_experiences: int = 0
    total_reward: float = 0.0

    # Decision source counts
    bot_decisions: int = 0
    brain_decisions: int = 0
    human_decisions: int = 0

    # Recent window metrics
    recent_successes: int = 0
    recent_failures: int = 0
    recent_rewards: List[float] = field(default_factory=list)

    # Learning progress
    consolidation_count: int = 0
    patterns_learned: int = 0

    # Performance history
    success_rate_history: List[float] = field(default_factory=list)
    reward_history: List[float] = field(default_factory=list)

    def get_success_rate(self) -> float:
        """Get overall success rate."""
        if self.total_experiences == 0:
            return 0.0
        return self.successful_experiences / self.total_experiences

    def get_recent_success_rate(self) -> float:
        """Get success rate in recent window."""
        total = self.recent_successes + self.recent_failures
        if total == 0:
            return 0.0
        return self.recent_successes / total

    def get_avg_reward(self) -> float:
        """Get average reward."""
        if self.total_experiences == 0:
            return 0.0
        return self.total_reward / self.total_experiences

    def record_experience(self, experience: Experience) -> None:
        """Record a new experience."""
        self.total_experiences += 1

        if experience.outcome == ExperienceOutcome.SUCCESS:
            self.successful_experiences += 1
            self.recent_successes += 1
        else:
            self.recent_failures += 1

        self.total_reward += experience.reward
        self.recent_rewards.append(experience.reward)

        # Keep recent window manageable
        if len(self.recent_rewards) > 100:
            self.recent_rewards.pop(0)


class ExperienceCollector:
    """Collects experiences from interactions."""

    def __init__(self, max_experiences: int = 10000):
        """
        Initialize the collector.

        Args:
            max_experiences: Maximum experiences to store
        """
        self.max_experiences = max_experiences
        self.experiences: List[Experience] = []
        self.experience_count = 0

    def collect(
        self,
        situation_type: str,
        situation_description: str,
        decision_source: DecisionSource,
        action_taken: str,
        outcome: ExperienceOutcome,
        reward: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Experience:
        """
        Collect a new experience.

        Args:
            situation_type: Type of situation
            situation_description: Description of the situation
            decision_source: Source of the decision
            action_taken: Action that was taken
            outcome: Outcome of the action
            reward: Reward value
            context: Additional context

        Returns:
            Collected experience
        """
        self.experience_count += 1

        experience = Experience(
            experience_id=f"exp_{self.experience_count:06d}",
            timestamp=datetime.now(),
            situation_type=situation_type,
            situation_description=situation_description,
            decision_source=decision_source,
            action_taken=action_taken,
            outcome=outcome,
            reward=reward,
            context=context or {},
        )

        self.experiences.append(experience)

        # Prune if over limit
        if len(self.experiences) > self.max_experiences:
            self.experiences.pop(0)

        return experience

    def get_recent(self, n: int = 100) -> List[Experience]:
        """Get n most recent experiences."""
        return self.experiences[-n:]

    def get_by_outcome(self, outcome: ExperienceOutcome) -> List[Experience]:
        """Get experiences with a specific outcome."""
        return [e for e in self.experiences if e.outcome == outcome]

    def get_by_situation_type(self, situation_type: str) -> List[Experience]:
        """Get experiences of a specific type."""
        return [e for e in self.experiences if e.situation_type == situation_type]


class ExperienceReplay:
    """Manages experience replay for learning."""

    def __init__(self, batch_size: int = 32, strategy: str = "prioritized"):
        """
        Initialize the replay buffer.

        Args:
            batch_size: Size of replay batches
            strategy: Replay strategy (random, prioritized, recent)
        """
        self.batch_size = batch_size
        self.strategy = strategy

    def sample_batch(self, experiences: List[Experience]) -> ReplayBatch:
        """
        Sample a batch of experiences for replay.

        Args:
            experiences: Available experiences to sample from

        Returns:
            Batch of experiences
        """
        if len(experiences) <= self.batch_size:
            batch_experiences = experiences
        else:
            if self.strategy == "random":
                batch_experiences = random.sample(experiences, self.batch_size)
            elif self.strategy == "recent":
                batch_experiences = experiences[-self.batch_size:]
            elif self.strategy == "prioritized":
                # Prioritize by reward magnitude (both positive and negative)
                scored = [
                    (e, abs(e.reward) + (1 if e.outcome != ExperienceOutcome.SUCCESS else 0))
                    for e in experiences
                ]
                scored.sort(key=lambda x: x[1], reverse=True)
                batch_experiences = [e for e, _ in scored[:self.batch_size]]
            else:
                batch_experiences = random.sample(experiences, self.batch_size)

        return ReplayBatch(
            experiences=batch_experiences,
            batch_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        )


class AdaptiveLearner:
    """Learns and adapts based on experiences."""

    def __init__(
        self,
        learning_rate: float = 0.1,
        target_success_rate: float = 0.85,
    ):
        """
        Initialize the learner.

        Args:
            learning_rate: How quickly to adapt
            target_success_rate: Target success rate for calibration
        """
        self.learning_rate = learning_rate
        self.target_success_rate = target_success_rate

        # Adaptive thresholds
        self.bot_threshold = 0.7
        self.brain_threshold = 0.5
        self.high_stakes_threshold = 0.7

        # Learning history
        self.threshold_history: List[Dict[str, float]] = []

    def learn_from_batch(self, batch: ReplayBatch, metrics: LearningMetrics) -> Dict[str, Any]:
        """
        Learn from a batch of experiences.

        Args:
            batch: Batch of experiences to learn from
            metrics: Current learning metrics

        Returns:
            Learning updates applied
        """
        updates = {}

        # Calculate current success rate
        current_success = batch.get_success_rate()
        avg_reward = batch.get_avg_reward()

        # Adjust thresholds based on performance
        if current_success < self.target_success_rate:
            # Success rate too low - be more conservative
            # Lower thresholds to escalate more often
            adjustment = self.learning_rate * (self.target_success_rate - current_success)

            updates["bot_threshold"] = self.bot_threshold - adjustment * 0.5
            updates["brain_threshold"] = self.brain_threshold - adjustment * 0.3

            # Apply updates
            self.bot_threshold = max(0.5, min(0.9, updates["bot_threshold"]))
            self.brain_threshold = max(0.3, min(0.7, updates["brain_threshold"]))

        elif current_success > self.target_success_rate + 0.1:
            # Success rate high - can be more aggressive
            # Raise thresholds to handle more at bot level
            adjustment = self.learning_rate * (current_success - self.target_success_rate)

            updates["bot_threshold"] = self.bot_threshold + adjustment * 0.3
            updates["brain_threshold"] = self.brain_threshold + adjustment * 0.2

            # Apply updates
            self.bot_threshold = max(0.5, min(0.9, updates["bot_threshold"]))
            self.brain_threshold = max(0.3, min(0.7, updates["brain_threshold"]))

        # Track history
        self.threshold_history.append({
            "bot_threshold": self.bot_threshold,
            "brain_threshold": self.brain_threshold,
            "success_rate": current_success,
            "avg_reward": avg_reward,
            "timestamp": datetime.now().isoformat(),
        })

        return updates

    def get_thresholds(self) -> Dict[str, float]:
        """Get current adaptive thresholds."""
        return {
            "bot_min_confidence": self.bot_threshold,
            "brain_min_confidence": self.brain_threshold,
            "high_stakes_threshold": self.high_stakes_threshold,
        }


class LearningLoop:
    """
    Complete learning loop combining collection, replay, consolidation,
    learning, and evaluation.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the learning loop."""
        # Load config (simplified - in real code would load from file)
        self.config = {
            "collection": {"max_experiences": 10000, "importance_threshold": 4.0},
            "replay": {"batch_size": 32, "strategy": "prioritized"},
            "learning": {"learning_rate": 0.1, "target_success_rate": 0.85},
            "evaluation": {"evaluate_every": 25},
        }

        # Initialize components
        self.memory = HierarchicalMemory(character_id="learning_agent")
        self.escalation = EscalationEngine()
        self.collector = ExperienceCollector(
            max_experiences=self.config["collection"]["max_experiences"],
        )
        self.replay = ExperienceReplay(
            batch_size=self.config["replay"]["batch_size"],
            strategy=self.config["replay"]["strategy"],
        )
        self.learner = AdaptiveLearner(
            learning_rate=self.config["learning"]["learning_rate"],
            target_success_rate=self.config["learning"]["target_success_rate"],
        )
        self.consolidation_engine = ConsolidationEngine()

        # Metrics
        self.metrics = LearningMetrics()

    def add_experience(
        self,
        situation_type: str,
        situation_description: str,
        decision_source: DecisionSource,
        action_taken: str,
        outcome: ExperienceOutcome,
        reward: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Experience:
        """
        Add a new experience to the learning loop.

        Returns:
            The created experience
        """
        # Collect experience
        experience = self.collector.collect(
            situation_type=situation_type,
            situation_description=situation_description,
            decision_source=decision_source,
            action_taken=action_taken,
            outcome=outcome,
            reward=reward,
            context=context,
        )

        # Update metrics
        self.metrics.record_experience(experience)

        # Store in memory
        importance = self.config["collection"]["importance_threshold"] + abs(reward)
        if outcome == ExperienceOutcome.FAILURE:
            importance += 2.0

        self.memory.store_episodic(
            f"{situation_type}: {situation_description[:80]}... Result: {outcome.value}",
            importance=importance,
            emotional_valence=reward,  # Use reward as emotional valence
        )

        # Track decision source counts
        if decision_source == DecisionSource.BOT:
            self.metrics.bot_decisions += 1
        elif decision_source == DecisionSource.BRAIN:
            self.metrics.brain_decisions += 1
        else:
            self.metrics.human_decisions += 1

        return experience

    def run_replay_cycle(self) -> Tuple[ReplayBatch, Dict[str, Any]]:
        """
        Run a replay and learning cycle.

        Returns:
            (batch, learning_updates)
        """
        experiences = self.collector.get_recent()
        if not experiences:
            return ReplayBatch([], "empty"), {}

        # Sample batch
        batch = self.replay.sample_batch(experiences)

        # Learn from batch
        updates = self.learner.learn_from_batch(batch, self.metrics)

        return batch, updates

    def consolidate_memories(self) -> Dict[str, int]:
        """
        Run memory consolidation.

        Returns:
            Counts of consolidated items
        """
        results = {"reflection": 0, "episodic_semantic": 0, "total": 0}

        # Reflection consolidation
        if self.memory.should_consolidate_reflection():
            result = self.consolidation_engine.consolidate(
                self.memory, strategy="reflection", force=True
            )
            results["reflection"] = result.output_count
            results["total"] += result.output_count

        # Episodic to semantic consolidation
        if self.memory.should_consolidate_episodic():
            result = self.consolidation_engine.consolidate(
                self.memory, strategy="episodic_semantic", force=True
            )
            results["episodic_semantic"] = result.output_count
            results["total"] += result.output_count

        self.metrics.consolidation_count += 1
        self.metrics.patterns_learned += results["total"]

        return results

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate current performance.

        Returns:
            Evaluation metrics
        """
        # Update success rate history
        self.metrics.success_rate_history.append(self.metrics.get_success_rate())

        # Calculate recent performance
        recent_rate = self.metrics.get_recent_success_rate()

        # Get thresholds
        thresholds = self.learner.get_thresholds()

        return {
            "total_experiences": self.metrics.total_experiences,
            "success_rate": self.metrics.get_success_rate(),
            "recent_success_rate": recent_rate,
            "avg_reward": self.metrics.get_avg_reward(),
            "decision_distribution": {
                "bot": self.metrics.bot_decisions,
                "brain": self.metrics.brain_decisions,
                "human": self.metrics.human_decisions,
            },
            "current_thresholds": thresholds,
            "consolidations": self.metrics.consolidation_count,
            "patterns_learned": self.metrics.patterns_learned,
        }

    def generate_report(self) -> str:
        """Generate a human-readable report."""
        eval_data = self.evaluate()

        report = []
        report.append("=" * 60)
        report.append("LEARNING LOOP REPORT")
        report.append("=" * 60)
        report.append("")
        report.append(f"Total Experiences: {eval_data['total_experiences']}")
        report.append(f"Success Rate: {eval_data['success_rate']:.1%}")
        report.append(f"Recent Success Rate: {eval_data['recent_success_rate']:.1%}")
        report.append(f"Average Reward: {eval_data['avg_reward']:+.2f}")
        report.append("")
        report.append("Decision Distribution:")
        for source, count in eval_data['decision_distribution'].items():
            pct = (count / eval_data['total_experiences'] * 100) if eval_data['total_experiences'] > 0 else 0
            report.append(f"  {source}: {count} ({pct:.1f}%)")
        report.append("")
        report.append("Current Thresholds:")
        for name, value in eval_data['current_thresholds'].items():
            report.append(f"  {name}: {value:.2f}")
        report.append("")
        report.append(f"Consolidations Run: {eval_data['consolidations']}")
        report.append(f"Patterns Learned: {eval_data['patterns_learned']}")
        report.append("")
        report.append("=" * 60)

        return "\n".join(report)
