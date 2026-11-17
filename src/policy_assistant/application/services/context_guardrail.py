
import re
from dataclasses import dataclass

from policy_assistant.domain.entities.chunk import Chunk


@dataclass(frozen=True)
class ContextGuardrailResult:
    safe_chunks: list[Chunk]
    rejected_count: int


class ContextGuardrail:
    """
    Validates retrieved document chunks for suspicious instructions.
    """

    INJECTION_PATTERNS = [
        # Attempts to override existing instructions
        re.compile(
            r"\b(ignore|disregard)\s+(all\s+)?"
            r"(previous|prior|above)\s+(instructions|directions)\b",
            re.IGNORECASE,
        ),

        # Attempts to change the assistant's role
        re.compile(
            r"\byou\s+are\s+now\s+(an?\s+)?"
            r"(unrestricted|unfiltered)\s+ai\b",
            re.IGNORECASE,
        ),

        # Attempts to extract hidden system instructions
        re.compile(
            r"\b(reveal|show|print|display)\s+"
            r"(your\s+)?(complete\s+|full\s+)?"
            r"(system\s+prompt|system\s+instructions)\b",
            re.IGNORECASE,
        ),
    ]

    def validate(self, chunks: list[Chunk]) -> ContextGuardrailResult:
        safe_chunks = []
        rejected_count = 0

        for chunk in chunks:
            if self._is_suspicious(chunk.content):
                rejected_count += 1
                continue

            safe_chunks.append(chunk)

        return ContextGuardrailResult(
            safe_chunks=safe_chunks,
            rejected_count=rejected_count,
        )

    def _is_suspicious(self, content: str) -> bool:
        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(content):
                return True

        return False
