import re

from policy_assistant.application.services.output_guardrail import (
    GuardrailResult,
)


class InputGuardrail:
    """
    Validates incoming user questions for suspicious prompt-injection patterns.
    """

    INJECTION_PATTERNS = [
        # Attempts to override existing instructions
        re.compile(
            r"\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b",
            re.IGNORECASE,
        ),

        # Attempts to change the assistant's role
        re.compile(
            r"\byou\s+are\s+now\s+(an?\s+)?(unrestricted|unfiltered)\s+ai\b",
            re.IGNORECASE,
        ),

        # Attempts to extract hidden system instructions
        re.compile(
            r"\b(reveal|show|print|display|repeat)\s+"
            r"(your\s+)?(complete\s+|full\s+)?"
            r"(system\s+prompt|system\s+instructions)\b",
            re.IGNORECASE,
        ),
    ]

    def validate(self, question: str) -> GuardrailResult:
        if not question or not question.strip():
            return GuardrailResult(
                is_safe=False,
                reason="Question cannot be empty.",
            )

        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(question):
                return GuardrailResult(
                    is_safe=False,
                    reason="Potential prompt injection detected.",
                )

        return GuardrailResult(is_safe=True)