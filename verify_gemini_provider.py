from policy_assistant.infrastructure.llm.gemini_llm_provider import (
    GeminiLLMProvider,
)

provider = GeminiLLMProvider()

context = """
Annual Leave Policy:
Employees receive 20 annual leaves.

Sick Leave Policy:
Employees receive 10 sick leaves.
"""

question = "How many annual leaves do employees receive?"

answer = provider.generate_answer(
    question=question,
    context=context,
)

print("\nQuestion:", question)
print("\nGemini Answer:", answer)

assert answer.strip()
assert "20" in answer

print("\nGemini integration test passed.")