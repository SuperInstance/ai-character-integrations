"""
Bot Rules for Customer Service

Pre-defined responses for common customer queries.
These provide instant, free responses for high-volume FAQs.
"""

from typing import Optional, Dict, List, Tuple
import re


class BotRule:
    """A single bot rule with pattern matching and response."""

    def __init__(
        self,
        name: str,
        patterns: List[str],
        response: str,
        confidence: float = 0.9,
        category: str = "general",
    ):
        """
        Initialize a bot rule.

        Args:
            name: Rule identifier
            patterns: List of regex patterns to match
            response: Response template
            confidence: Confidence in this response (0-1)
            category: Category for reporting
        """
        self.name = name
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.response = response
        self.confidence = confidence
        self.category = category

    def matches(self, text: str) -> Tuple[bool, float]:
        """
        Check if this rule matches the input.

        Returns:
            (matches, confidence) tuple
        """
        for pattern in self.patterns:
            if pattern.search(text):
                return True, self.confidence
        return False, 0.0

    def get_response(self, context: Optional[Dict] = None) -> str:
        """
        Get the response for this rule.

        Args:
            context: Optional context variables for template substitution

        Returns:
            Formatted response
        """
        response = self.response
        if context:
            for key, value in context.items():
                response = response.replace(f"{{{key}}}", str(value))
        return response


class BotRulesEngine:
    """
    Engine for managing and applying bot rules.

    Provides instant responses for common queries without
    incurring LLM costs.
    """

    def __init__(self):
        """Initialize the rules engine with default rules."""
        self.rules: List[BotRule] = []
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load default customer service rules."""
        self.rules = [
            # Password/Account Access
            BotRule(
                name="password_reset",
                patterns=[
                    r"password.*reset",
                    r"forgot.*password",
                    r"can't.*login",
                    r"cannot.*log.*in",
                    r"reset.*password",
                ],
                response=(
                    "I can help you reset your password. Please visit our password reset page "
                    "at https://example.com/reset-password and follow the instructions. "
                    "You'll receive an email with a reset link shortly. Is there anything else "
                    "I can help you with?"
                ),
                confidence=0.95,
                category="account",
            ),

            # Billing/Payments
            BotRule(
                name="billing_inquiry",
                patterns=[
                    r"billing",
                    r"invoice",
                    r"charge.*card",
                    r"payment.*issue",
                    r"refund",
                ],
                response=(
                    "I'd be happy to help with your billing inquiry. To better assist you, "
                    "could you please provide your account number or the email associated "
                    "with your account? For immediate viewing of invoices, you can also visit "
                    "your account dashboard at https://example.com/account/billing."
                ),
                confidence=0.90,
                category="billing",
            ),

            BotRule(
                name="refund_request",
                patterns=[
                    r"want.*refund",
                    r"request.*refund",
                    r"get.*money.*back",
                    r"chargeback",
                ],
                response=(
                    "I understand you'd like a refund. Refund requests are reviewed "
                    "within 1-2 business days. To submit a formal refund request, please "
                    "visit https://example.com/refund or provide your order number and I "
                    "can help initiate the process."
                ),
                confidence=0.85,
                category="billing",
            ),

            # Technical Support
            BotRule(
                name="basic_troubleshooting",
                patterns=[
                    r"not working",
                    r"doesn't work",
                    r"can't access",
                    r"error.*message",
                    r"something wrong",
                ],
                response=(
                    "I'm sorry to hear you're experiencing issues. Let me help you troubleshoot. "
                    "First, could you tell me: 1) What specifically isn't working? 2) When did "
                    "the problem start? 3) Are you seeing any error messages? Meanwhile, please "
                    "try clearing your browser cache and cookies, which resolves many common issues."
                ),
                confidence=0.75,
                category="technical",
            ),

            BotRule(
                name="slow_performance",
                patterns=[
                    r"slow",
                    r"lagging",
                    r"taking.*long",
                    r"performance",
                ],
                response=(
                    "I understand things seem slow. Performance issues can be caused by several "
                    "factors. Please check: 1) Your internet connection speed 2) Browser extensions "
                    "that might be interfering 3) Whether you're using a supported browser. We "
                    "recommend Chrome, Firefox, or Safari for the best experience."
                ),
                confidence=0.80,
                category="technical",
            ),

            # Account Management
            BotRule(
                name="account_info",
                patterns=[
                    r"account.*information",
                    r"update.*profile",
                    r"change.*email",
                    r"change.*password",
                ],
                response=(
                    "You can update your account information by visiting your account settings "
                    "at https://example.com/account/settings. There you can change your email, "
                    "password, notification preferences, and more. Is there a specific setting "
                    "you're having trouble finding?"
                ),
                confidence=0.90,
                category="account",
            ),

            BotRule(
                name="cancel_account",
                patterns=[
                    r"cancel.*account",
                    r"delete.*account",
                    r"close.*account",
                    r"unsubscribe",
                ],
                response=(
                    "I'm sorry to see you go. Before you cancel, I'd like to understand if there's "
                    "a specific issue we could help resolve. If you still wish to cancel, please "
                    "visit https://example.com/account/cancel or confirm your account details and "
                    "I can guide you through the process. Note that cancellations take effect at "
                    "the end of your current billing period."
                ),
                confidence=0.95,
                category="account",
            ),

            # Features/Functionality
            BotRule(
                name="feature_request",
                patterns=[
                    r"can.*you.*do",
                    r"is.*it.*possible",
                    r"how.*do.*i",
                    r"feature",
                ],
                response=(
                    "Thanks for your interest in our features! Let me help you understand what's "
                    "available. Could you be more specific about what you're trying to accomplish? "
                    "I can then provide the most relevant information or alternative solutions."
                ),
                confidence=0.70,
                category="general",
            ),

            # Pricing/Plans
            BotRule(
                name="pricing_inquiry",
                patterns=[
                    r"how much",
                    r"pricing",
                    r"cost.*plan",
                    r"subscription",
                    r"upgrade.*plan",
                ],
                response=(
                    "We offer several plans to fit different needs: Basic ($9/month), Pro "
                    "($29/month), and Enterprise (custom pricing). Each plan includes different "
                    "features and usage limits. You can compare all plans and upgrade at "
                    "https://example.com/pricing. Would you like me to explain the differences?"
                ),
                confidence=0.90,
                category="sales",
            ),

            # Contact Hours
            BotRule(
                name="contact_hours",
                patterns=[
                    r"hours",
                    r"when.*open",
                    r"customer service.*hours",
                    r"support.*hours",
                ],
                response=(
                    "Our customer support is available Monday through Friday, 6:00 AM to 6:00 PM "
                    "Pacific Time. Emergency support is available 24/7 for Enterprise customers. "
                    "You can also reach us via email at support@example.com for non-urgent matters."
                ),
                confidence=0.95,
                category="general",
            ),

            # Greetings
            BotRule(
                name="greeting",
                patterns=[
                    r"^hello",
                    r"^hi ",
                    r"^hey",
                    r"^good morning",
                    r"^good afternoon",
                ],
                response=(
                    "Hello! Welcome to our customer service. How can I help you today? I can assist "
                    "with account questions, technical issues, billing inquiries, and more."
                ),
                confidence=0.90,
                category="general",
            ),

            # Thank you
            BotRule(
                name="thanks",
                patterns=[
                    r"thank",
                    r"thanks",
                    r"appreciate",
                ],
                response=(
                    "You're welcome! Is there anything else I can help you with today?"
                ),
                confidence=0.95,
                category="general",
            ),

            # Goodbye
            BotRule(
                name="goodbye",
                patterns=[
                    r"bye",
                    r"goodbye",
                    r"that.*all",
                ],
                response=(
                    "Thank you for contacting us! If you need anything else in the future, "
                    "please don't hesitate to reach out. Have a great day!"
                ),
                confidence=0.95,
                category="general",
            ),
        ]

    def add_rule(self, rule: BotRule) -> None:
        """Add a new rule to the engine."""
        self.rules.append(rule)

    def find_match(self, text: str, min_confidence: float = 0.7) -> Optional[BotRule]:
        """
        Find the best matching rule for the given text.

        Args:
            text: Customer query text
            min_confidence: Minimum confidence threshold

        Returns:
            Best matching BotRule or None
        """
        best_rule = None
        best_confidence = min_confidence

        for rule in self.rules:
            matches, confidence = rule.matches(text)
            if matches and confidence > best_confidence:
                best_rule = rule
                best_confidence = confidence

        return best_rule

    def get_response(
        self,
        text: str,
        context: Optional[Dict] = None,
        min_confidence: float = 0.7,
    ) -> Tuple[bool, Optional[str], float]:
        """
        Get a bot response for the given text.

        Args:
            text: Customer query text
            context: Optional context for template substitution
            min_confidence: Minimum confidence threshold

        Returns:
            (handled, response, confidence) tuple
        """
        rule = self.find_match(text, min_confidence)

        if rule:
            response = rule.get_response(context)
            return True, response, rule.confidence

        return False, None, 0.0

    def get_stats(self) -> Dict:
        """Get statistics about loaded rules."""
        categories = {}
        for rule in self.rules:
            cat = rule.category
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        return {
            "total_rules": len(self.rules),
            "categories": categories,
            "avg_confidence": sum(r.confidence for r in self.rules) / len(self.rules),
        }


# Global instance
_bot_engine = None


def get_bot_engine() -> BotRulesEngine:
    """Get the global bot rules engine instance."""
    global _bot_engine
    if _bot_engine is None:
        _bot_engine = BotRulesEngine()
    return _bot_engine
