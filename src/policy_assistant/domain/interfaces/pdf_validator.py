from typing import Protocol


class PDFValidator(Protocol):

    def validate(self, file_path: str) -> None:
        ...