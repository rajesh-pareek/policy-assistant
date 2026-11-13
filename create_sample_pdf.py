
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import (
    DictionaryObject,
    NameObject,
    NumberObject,
    ArrayObject,
    DecodedStreamObject,
)

writer = PdfWriter()

def add_text_page(text: str):
    page = writer.add_blank_page(width=612, height=792)

    stream = DecodedStreamObject()
    stream.set_data(
        f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode("ascii")
    )

    page[NameObject("/Contents")] = writer._add_object(stream)

    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({
            NameObject("/F1"): DictionaryObject({
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            })
        })
    })

add_text_page("Annual Leave Policy: Employees receive 20 annual leaves.")
add_text_page("Sick Leave Policy: Employees receive 10 sick leaves.")

output = Path("sample_documents/test_policy.pdf")
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("wb") as file:
    writer.write(file)

print(f"Sample PDF created: {output}")
