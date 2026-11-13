
import math

from policy_assistant.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)

provider = SentenceTransformerEmbeddingProvider()

texts = [
    "Employees receive 20 annual leaves.",
    "Employees receive 10 sick leaves.",
]

embeddings = provider.embed_texts(texts)

print("Number of embeddings:", len(embeddings))

for index, embedding in enumerate(embeddings):
    magnitude = math.sqrt(sum(value * value for value in embedding))

    print(f"\nEmbedding {index + 1}:")
    print("Dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])
    print("Magnitude:", magnitude)

    assert len(embedding) == 384
    assert abs(magnitude - 1.0) < 0.001

single_embedding = provider.embed_text("Employees receive 20 annual leaves.")

assert len(single_embedding) == 384

print("\nSingle-text embedding: Successful")
print("All embedding verification checks passed.")
