
from pathlib import Path


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class PDFValidator:

    def validate(self, file_path: str) -> None:

        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise ValueError("PDF file does not exist.")

        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are allowed.")

        if path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError("PDF file exceeds the 10 MB limit.")

        with path.open("rb") as file:
            signature = file.read(5)

        if signature != b"%PDF-":
            raise ValueError("Invalid PDF file signature.")
