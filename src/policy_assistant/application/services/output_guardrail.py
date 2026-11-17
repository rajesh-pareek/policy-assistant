
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    is_safe: bool
    reason: str | None = None


class OutputGuardrail:
    """
    Validates generated answers before they are returned to users.
    """

    SECRET_PATTERNS = [
        # Gemini API keys
        re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),

        # AWS access key IDs
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),

        # Bearer tokens
        re.compile(
            r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}",
            re.IGNORECASE,
        ),

        # Credentials and secrets assigned in text
        re.compile(
            r"\b(?:password|passwd|api[_-]?key|"
            r"client[_-]?secret|access[_-]?token|"
            r"auth[_-]?token|secret)\b"
            r"\s*[:=]\s*['\"]?[^\s,'\";]{4,}",
            re.IGNORECASE,
        ),
    ]

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    # Indian mobile numbers, optionally prefixed with +91
    PHONE_PATTERN = re.compile(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
    )

    def __init__(self, allowed_emails: set[str] | None = None):
        self.allowed_emails = {
            email.strip().lower()
            for email in (allowed_emails or set())
        }

    def validate(self, answer: str) -> GuardrailResult:
        if not answer or not answer.strip():
            return GuardrailResult(
                is_safe=False,
                reason="Generated answer is empty.",
            )

        # Check for secrets and credentials.
        for pattern in self.SECRET_PATTERNS:
            if pattern.search(answer):
                return GuardrailResult(
                    is_safe=False,
                    reason="Potential secret or credential detected.",
                )

        # Check email addresses against the approved allowlist.
        emails = self.EMAIL_PATTERN.findall(answer)

        for email in emails:
            if email.lower() not in self.allowed_emails:
                return GuardrailResult(
                    is_safe=False,
                    reason="Unapproved email address detected.",
                )

        # Block phone numbers by default.
        if self.PHONE_PATTERN.search(answer):
            return GuardrailResult(
                is_safe=False,
                reason="Potential phone number detected.",
            )

        return GuardrailResult(is_safe=True)
