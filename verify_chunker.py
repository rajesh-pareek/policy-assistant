
from uuid import uuid4

from policy_assistant.domain.entities.extracted_page import ExtractedPage
from policy_assistant.infrastructure.chunking.token_chunker import TokenChunker


chunker = TokenChunker()
document_id = uuid4()

pages = [
    ExtractedPage(
        page_number=1,
        content=" ".join(f"annual leave policy section {i}" for i in range(300)),
    ),
    ExtractedPage(
        page_number=2,
        content=" ".join(f"sick leave policy section {i}" for i in range(300)),
    ),
    ExtractedPage(
        page_number=3,
        content="   ",
    ),
]

chunks = chunker.create_chunks(pages, document_id)

print("Total chunks:", len(chunks))

for chunk in chunks:
    token_count = len(chunker.encoding.encode(chunk.content))
    print(
        f"Chunk: {chunk.chunk_index} | "
        f"Page: {chunk.page_number} | "
        f"Tokens: {token_count}"
    )

assert len(chunks) > 2
assert all(
    len(chunker.encoding.encode(chunk.content)) <= 500
    for chunk in chunks
)
assert all(chunk.document_id == document_id for chunk in chunks)
assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
assert all(chunk.page_number in (1, 2) for chunk in chunks)

for previous, current in zip(chunks, chunks[1:]):
    if previous.page_number == current.page_number:
        previous_tokens = chunker.encoding.encode(previous.content)
        current_tokens = chunker.encoding.encode(current.content)
        assert previous_tokens[-50:] == current_tokens[:50]

print("\nAll chunking verification checks passed.")
