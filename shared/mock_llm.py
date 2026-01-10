"""
Mock LLM Provider for Integration Examples

This module provides a mock LLM provider that simulates responses from
various LLM providers without requiring actual API calls or credits.

Use this for testing and development without incurring API costs.
"""

import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LLMProviderType(Enum):
    """Types of LLM providers we can mock."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class MockResponse:
    """Mock LLM response."""
    content: str
    tokens_used: int
    cost_estimate: float
    latency_ms: float


class MockLLMProvider:
    """
    Mock LLM provider that simulates responses without API calls.

    This is useful for:
    - Development and testing
    - Demonstrations without API costs
    - Reproducible examples
    """

    def __init__(
        self,
        provider: LLMProviderType = LLMProviderType.OPENAI,
        model: str = "gpt-4",
        latency_range: tuple = (100, 500),
    ):
        """
        Initialize the mock provider.

        Args:
            provider: The type of provider to mock
            model: The model name to simulate
            latency_range: (min, max) latency in milliseconds
        """
        self.provider = provider
        self.model = model
        self.latency_range = latency_range
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0

        # Cost per 1k tokens by provider type
        self.cost_per_1k = {
            LLMProviderType.OPENAI: 0.03,
            LLMProviderType.ANTHROPIC: 0.015,
            LLMProviderType.OLLAMA: 0.0,
        }

    def _calculate_latency(self) -> float:
        """Calculate simulated latency."""
        return random.uniform(*self.latency_range)

    def _calculate_tokens(self, prompt: str, response: str) -> int:
        """Estimate token count (rough approximation: 1 token ~ 4 chars)."""
        return (len(prompt) + len(response)) // 4

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on tokens."""
        return (tokens / 1000) * self.cost_per_1k[self.provider]

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> MockResponse:
        """
        Generate a mock completion.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (affects response randomness)
            max_tokens: Maximum tokens to generate

        Returns:
            MockResponse with generated content
        """
        self.request_count += 1

        # Simulate network latency
        latency = self._calculate_latency()
        time.sleep(latency / 1000)

        # Generate a contextually relevant response
        response = self._generate_response(prompt, system_prompt, temperature)

        # Calculate metrics
        tokens = self._calculate_tokens(prompt, response)
        cost = self._calculate_cost(tokens)

        self.total_tokens += tokens
        self.total_cost += cost

        return MockResponse(
            content=response,
            tokens_used=tokens,
            cost_estimate=cost,
            latency_ms=latency,
        )

    def _generate_response(
        self, prompt: str, system_prompt: Optional[str], temperature: float
    ) -> str:
        """Generate a mock response based on the prompt."""

        # Extract keywords from prompt for contextual responses
        prompt_lower = prompt.lower()

        # Customer service responses
        if any(word in prompt_lower for word in ["refund", "billing", "charge"]):
            return self._billing_response(prompt_lower)

        # Technical support responses
        if any(word in prompt_lower for word in ["error", "bug", "crash", "not working"]):
            return self._technical_response(prompt_lower)

        # General queries
        if any(word in prompt_lower for word in ["help", "how", "what", "explain"]):
            return self._explanation_response(prompt_lower)

        # Default generic response
        return self._generic_response(prompt, temperature)

    def _billing_response(self, prompt: str) -> str:
        """Generate billing-related responses."""
        responses = [
            "I understand your concern about the billing issue. Let me look into that for you. Based on your account, I can see the charge in question. This appears to be for your monthly subscription. Would you like me to explain the breakdown of this charge?",
            "I'd be happy to help you with your refund request. I can process this for you right away. The refund should appear on your original payment method within 5-7 business days. Is there anything else I can assist you with?",
            "Regarding your billing question, I've reviewed your account and everything looks correct on our end. The charge you're seeing is for the premium plan you selected last month. Would you like me to send you a detailed invoice?",
        ]
        return random.choice(responses)

    def _technical_response(self, prompt: str) -> str:
        """Generate technical support responses."""
        responses = [
            "I see you're experiencing a technical issue. Let me help you troubleshoot this. First, could you please try clearing your browser cache and cookies? This resolves many common issues. If the problem persists, please let me know the exact error message you're seeing.",
            "Thank you for reporting this bug. Our engineering team has been notified and is investigating the issue. In the meantime, here's a workaround that should help you continue using the service: [try refreshing the page or using a different browser].",
            "I apologize for the inconvenience you're experiencing. Based on your description, this sounds like it might be a connectivity issue. Please check your internet connection and try again. If you're still having trouble, our technical support team is available 24/7 to assist you.",
        ]
        return random.choice(responses)

    def _explanation_response(self, prompt: str) -> str:
        """Generate explanation responses."""
        responses = [
            "Great question! Let me explain how this works. The system is designed to intelligently route your requests based on various factors like complexity, urgency, and your past interactions. This ensures you get the most efficient and relevant support possible.",
            "I'd be happy to help clarify that. Essentially, this feature allows you to customize your experience based on your preferences. You can access these settings from your profile page. Would you like me to walk you through the specific options available?",
            "That's an excellent question. Here's what you need to know: our system uses advanced algorithms to understand your needs and provide personalized assistance. The more you interact with the system, the better it becomes at anticipating your requirements.",
        ]
        return random.choice(responses)

    def _generic_response(self, prompt: str, temperature: float) -> str:
        """Generate generic responses based on temperature."""
        if temperature < 0.3:
            # Low temperature = more predictable
            return "I understand your request. I'm processing this now and will provide you with the most relevant information based on your query. Please let me know if you need any additional assistance."

        elif temperature > 0.8:
            # High temperature = more creative
            return "Fascinating query! I love exploring these kinds of questions. There are so many interesting angles we could take here. Let me share some thoughts that might spark new ideas for you. The possibilities are truly endless when we dive deep into topics like this!"

        else:
            # Medium temperature = balanced
            return "Thank you for your message. I've reviewed your request and I'm here to help. Based on what you've shared, I can provide some guidance. Please let me know if you'd like more details on any particular aspect of this."

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> MockResponse:
        """
        Generate a mock chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            MockResponse with generated content
        """
        # Build a prompt from the message history
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role}: {content}")

        combined_prompt = "\n".join(prompt_parts)

        # Get the last message as the primary prompt
        last_message = messages[-1].get("content", "") if messages else ""

        return self.complete(last_message, combined_prompt, temperature, max_tokens)

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "provider": self.provider.value,
            "model": self.model,
        }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0


class MockLLMFactory:
    """Factory for creating mock LLM providers."""

    _providers: Dict[str, MockLLMProvider] = {}

    @classmethod
    def get_provider(
        cls,
        provider: LLMProviderType = LLMProviderType.OPENAI,
        model: str = "gpt-4",
        latency_range: tuple = (100, 500),
    ) -> MockLLMProvider:
        """Get or create a mock provider instance."""
        key = f"{provider.value}:{model}"

        if key not in cls._providers:
            cls._providers[key] = MockLLMProvider(provider, model, latency_range)

        return cls._providers[key]

    @classmethod
    def reset_all(cls) -> None:
        """Reset all providers."""
        cls._providers.clear()


# Convenience function for quick usage
def mock_complete(
    prompt: str,
    provider: LLMProviderType = LLMProviderType.OPENAI,
    temperature: float = 0.7,
) -> str:
    """
    Quick completion function for simple use cases.

    Args:
        prompt: The prompt to complete
        provider: The type of provider to use
        temperature: Sampling temperature

    Returns:
        Generated response text
    """
    llm = MockLLMFactory.get_provider(provider)
    response = llm.complete(prompt, temperature=temperature)
    return response.content
