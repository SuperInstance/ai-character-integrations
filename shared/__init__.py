"""
Shared Utilities Package

Common utilities and mock providers for integration examples.
"""

from .mock_llm import (
    MockLLMProvider,
    MockLLMFactory,
    MockResponse,
    LLMProviderType,
    mock_complete,
)

from .utils import (
    load_config,
    get_default_config,
    ensure_data_dir,
    format_timestamp,
    print_section,
    print_subsection,
    print_memory,
    print_decision,
    simulate_delay,
    ProgressTracker,
    prompt_user,
    confirm,
    sanitize_id,
    truncate,
    extract_keywords,
)

__all__ = [
    # Mock LLM
    "MockLLMProvider",
    "MockLLMFactory",
    "MockResponse",
    "LLMProviderType",
    "mock_complete",
    # Utils
    "load_config",
    "get_default_config",
    "ensure_data_dir",
    "format_timestamp",
    "print_section",
    "print_subsection",
    "print_memory",
    "print_decision",
    "simulate_delay",
    "ProgressTracker",
    "prompt_user",
    "confirm",
    "sanitize_id",
    "truncate",
    "extract_keywords",
]
