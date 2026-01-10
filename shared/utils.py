"""
Shared Utilities for Integration Examples

Common helper functions and utilities used across examples.
"""

import os
import json
import yaml
from typing import Any, Dict, Optional, List
from pathlib import Path
from datetime import datetime


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    path = Path(config_path)

    if not path.exists():
        # Return default config if file doesn't exist
        return get_default_config()

    with open(path, "r") as f:
        if path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif path.suffix == ".json":
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "escalation": {
            "bot_min_confidence": 0.7,
            "brain_min_confidence": 0.5,
            "high_stakes_threshold": 0.7,
            "critical_stakes_threshold": 0.9,
            "urgent_time_ms": 500,
            "critical_time_ms": 100,
        },
        "memory": {
            "max_working_memories": 10,
            "max_mid_term_memories": 100,
            "recency_decay_rate": 0.995,
            "consolidation_threshold": 150.0,
        },
        "llm": {
            "provider": "mock",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 500,
            "latency_range": [100, 500],
        },
    }


def ensure_data_dir(character_id: str, base_dir: str = "./data") -> Path:
    """
    Ensure data directory exists for a character.

    Args:
        character_id: Character identifier
        base_dir: Base directory for data storage

    Returns:
        Path to the character's data directory
    """
    data_dir = Path(base_dir) / character_id
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime for display.

    Args:
        dt: Datetime to format (defaults to now)

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def print_section(title: str, width: int = 60) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")


def print_subsection(title: str, width: int = 40) -> None:
    """Print a formatted subsection header."""
    print("\n" + "-" * width)
    print(title)
    print("-" * width)


def print_memory(memory, show_details: bool = False) -> None:
    """
    Print a memory in a formatted way.

    Args:
        memory: Memory object to print
        show_details: Whether to show detailed information
    """
    icon = get_memory_icon(memory.memory_type.value)
    print(f"  {icon} [{memory.memory_type.value.upper()}] {memory.content[:70]}...")

    if show_details:
        print(f"     Importance: {memory.importance:.1f} | Accessed: {memory.access_count}x")
        if hasattr(memory, "emotional_valence"):
            ev = memory.emotional_valence
            emoji = get_emoji_from_valence(ev)
            print(f"     Emotional: {ev:+.2f} {emoji}")


def get_memory_icon(memory_type: str) -> str:
    """Get an icon for a memory type."""
    icons = {
        "working": "  ",
        "mid_term": "  ",
        "long_term": "  ",
        "episodic": "  ",
        "semantic": "  ",
        "procedural": "  ",
    }
    return icons.get(memory_type, "  ")


def get_emoji_from_valence(valence: float) -> str:
    """Get emoji based on emotional valence."""
    if valence > 0.5:
        return ""
    elif valence > 0:
        return ""
    elif valence > -0.3:
        return ""
    else:
        return ""


def print_decision(decision) -> None:
    """
    Print an escalation decision in a formatted way.

    Args:
        decision: EscalationDecision object
    """
    source_icons = {
        "BOT": "  ",
        "BRAIN": "  ",
        "HUMAN": "  ",
    }

    icon = source_icons.get(decision.source.value, "  ")
    print(f"  {icon} Route: {decision.source.value.upper()}")
    print(f"     Reason: {decision.reason.value if decision.reason else 'N/A'}")
    print(f"     Confidence Required: {decision.confidence_required:.2f}")


def simulate_delay(min_ms: int = 50, max_ms: int = 200) -> None:
    """
    Simulate a processing delay for realism.

    Args:
        min_ms: Minimum delay in milliseconds
        max_ms: Maximum delay in milliseconds
    """
    import time
    import random
    delay = random.randint(min_ms, max_ms) / 1000
    time.sleep(delay)


class ProgressTracker:
    """Track and display progress for long-running operations."""

    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize the progress tracker.

        Args:
            total: Total number of items to process
            description: Description of the operation
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()

    def update(self, n: int = 1) -> None:
        """
        Update progress.

        Args:
            n: Number of items completed
        """
        self.current += n
        self._display()

    def _display(self) -> None:
        """Display current progress."""
        percent = (self.current / self.total) * 100
        bar_length = 40
        filled = int(bar_length * self.current / self.total)
        bar = "" * filled + "" * (bar_length - filled)

        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / rate if rate > 0 else 0

        print(
            f"\r{self.description}: [{bar}] {self.current}/{self.total} "
            f"({percent:.1f}%) ETA: {eta:.0f}s",
            end="",
            flush=True,
        )

        if self.current >= self.total:
            print()  # New line when complete

    def finish(self) -> None:
        """Mark progress as complete."""
        self.current = self.total
        self._display()


def prompt_user(prompt: str, default: Optional[str] = None) -> str:
    """
    Prompt user for input with optional default.

    Args:
        prompt: The prompt message
        default: Default value if user presses enter

    Returns:
        User input or default
    """
    if default is not None:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "

    response = input(full_prompt).strip()

    if not response and default is not None:
        return default

    return response


def confirm(prompt: str, default: bool = True) -> bool:
    """
    Ask user for yes/no confirmation.

    Args:
        prompt: The prompt message
        default: Default response if user presses enter

    Returns:
        True if user confirms, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ["y", "yes"]


def sanitize_id(id_string: str) -> str:
    """
    Sanitize a string for use as an identifier.

    Args:
        id_string: String to sanitize

    Returns:
        Sanitized identifier
    """
    import re
    # Remove non-alphanumeric characters except underscore and hyphen
    return re.sub(r"[^a-zA-Z0-9_-]", "_", id_string)


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract simple keywords from text (very basic implementation).

    Args:
        text: Text to extract from
        top_n: Number of keywords to return

    Returns:
        List of keywords
    """
    import re
    from collections import Counter

    # Simple word extraction
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

    # Filter out common words
    stopwords = {
        "this", "that", "with", "from", "have", "been", "were", "they",
        "what", "when", "where", "will", "just", "like", "more", " some"
    }

    words = [w for w in words if w not in stopwords]

    # Return most common
    counter = Counter(words)
    return [w for w, _ in counter.most_common(top_n)]
