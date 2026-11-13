from typing import Protocol


class LLMProvider(Protocol):

    def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        ...