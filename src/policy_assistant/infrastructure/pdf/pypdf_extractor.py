
from pypdf import PdfReader

from policy_assistant.domain.entities.extracted_page import ExtractedPage


class PyPDFExtractor:

    def extract(self, file_path: str) -> list[ExtractedPage]:

        reader = PdfReader(file_path)

        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported.")

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            content = page.extract_text() or ""

            pages.append(
                ExtractedPage(
                    page_number=page_number,
                    content=content,
                )
            )

        if not any(page.content.strip() for page in pages):
            raise ValueError("PDF contains no extractable text.")

        return pages
