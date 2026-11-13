from typing import Protocol

from policy_assistant.domain.entities.extracted_page import ExtractedPage


class PDFExtractor(Protocol):

    def extract(self, file_path: str) -> list[ExtractedPage]:
        ...